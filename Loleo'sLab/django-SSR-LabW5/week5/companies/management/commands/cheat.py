# In your_app/management/commands/suggest_queries.py

from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import models
from django.db.models.fields.reverse_related import ManyToManyRel, ManyToOneRel, OneToOneRel
from pathlib import Path
import re

class Command(BaseCommand):
    help = 'Analyzes all Django models and suggests comprehensive queries including ManyToMany bridge tables and FK relationships.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--app', 
            type=str, 
            help='Analyze only models from this specific app'
        )
        parser.add_argument(
            '--model', 
            type=str, 
            help='Analyze only this specific model (requires --app)'
        )
        parser.add_argument(
            '--include-django', 
            action='store_true',
            help='Include Django built-in models (auth, admin, etc.)'
        )

    def handle(self, *args, **kwargs):
        app_name = kwargs.get('app')
        model_name = kwargs.get('model')
        include_django = kwargs.get('include_django', False)

        # Prepare markdown output collection
        result_path = Path.cwd() / 'result.md'
        original_stdout_write = self.stdout.write
        self._result_lines = []

        def buffer_write(s=''):
            if s is None:
                s = ''
            if not isinstance(s, str):
                s = str(s)
            # strip trailing newlines here to normalize
            self._result_lines.append(s.rstrip('\n'))

        # Redirect writes to buffer
        self.stdout.write = buffer_write

        if model_name and not app_name:
            self.stdout.write(self.style.ERROR("Error: --model requires --app to be specified."))
            # restore and write file below
        

        # Get all models or filter by app/model
        if app_name and model_name:
            try:
                model = apps.get_model(app_name, model_name.capitalize())
                models_to_analyze = [model]
            except LookupError:
                self.stdout.write(self.style.ERROR(f"Error: Model '{model_name}' not found in app '{app_name}'."))
                return
        else:
            models_to_analyze = []
            for model in apps.get_models():
                app_label = model._meta.app_label
                
                # Filter by app if specified
                if app_name and app_label != app_name:
                    continue
                
                # Skip Django built-in models unless requested
                if not include_django and app_label in ['auth', 'admin', 'contenttypes', 'sessions']:
                    continue
                
                models_to_analyze.append(model)

        if not models_to_analyze:
            self.stdout.write(self.style.WARNING("No models found to analyze."))
        else:
            # Track bridge tables to avoid duplicates
            bridge_tables_analyzed = set()

            for model in models_to_analyze:
                self.analyze_model(model, bridge_tables_analyzed)

        # Post-process buffer into Markdown and write file
        try:
            ansi_re = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
            cleaned = [ansi_re.sub('', line) for line in self._result_lines]

            md_lines = []
            in_code = False
            current_model = None

            def close_code():
                nonlocal in_code
                if in_code:
                    md_lines.append('```')
                    md_lines.append('')  # Add spacing after code blocks
                    in_code = False

            def add_toc():
                # Generate table of contents
                toc_lines = ['# Django Model Query Guide\n', '## Table of Contents\n']
                model_names = []
                for line in cleaned:
                    if 'MODEL:' in line:
                        model_match = re.search(r'MODEL:\s*(\w+)', line)
                        if model_match:
                            model_names.append(model_match.group(1))
                
                for model in model_names:
                    toc_lines.append(f'- [{model}](#{model.lower()})')
                
                toc_lines.extend(['', '---', ''])
                return toc_lines

            # Add table of contents
            md_lines.extend(add_toc())

            for line in cleaned:
                stripped = line.strip()
                if not stripped:
                    close_code()
                    md_lines.append('')
                    continue

                # long separator -> enhanced model separator
                if set(stripped) <= set('=') and len(stripped) > 3:
                    close_code()
                    if current_model:
                        md_lines.extend(['', '---', ''])  # More spacing between models
                    continue

                # MODEL header - enhanced with emoji and better formatting
                if 'MODEL:' in stripped:
                    close_code()
                    # Extract model name and path
                    model_match = re.search(r'MODEL:\s*(\w+)\s*\(([^)]+)\)', stripped)
                    if model_match:
                        model_name = model_match.group(1)
                        model_path = model_match.group(2)
                        current_model = model_name
                        md_lines.extend([
                            f'## 📋 {model_name}',
                            f'> **Module**: `{model_path}`',
                            ''
                        ])
                    else:
                        md_lines.append('## ' + stripped.replace('MODEL:', '').strip())
                    continue

                # Table info - enhanced styling
                if stripped.startswith('Table:'):
                    close_code()
                    table_name = stripped.replace('Table:', '').strip()
                    md_lines.extend([
                        f'**🗃️ Database Table**: `{table_name}`',
                        ''
                    ])
                    continue

                # Field headers - make them more prominent
                if stripped.startswith("# Field:"):
                    close_code()
                    # Extract field name and type
                    field_match = re.search(r"Field:\s*'([^']+)'\s*\(Type:\s*([^)]+)\)", stripped)
                    if field_match:
                        field_name = field_match.group(1)
                        field_type = field_match.group(2)
                        md_lines.extend([
                            f'### 🔧 Field: `{field_name}`',
                            f'**Type**: `{field_type}`',
                            ''
                        ])
                    else:
                        md_lines.append('### ' + stripped[1:].strip())
                    continue

                # Reverse relationship headers
                if stripped.startswith('# Reverse Relation:'):
                    close_code()
                    md_lines.extend([
                        f'### 🔗 {stripped[2:].strip()}',
                        ''
                    ])
                    continue

                # Comment headings - categorize them better
                if stripped.startswith('#'):
                    close_code()
                    content = stripped[1:].strip()
                    
                    # Categorize different types of sections
                    if 'Basic Model Queries' in content:
                        md_lines.extend([
                            '### 🚀 Basic Model Queries',
                            ''
                        ])
                    elif 'Aggregation Examples' in content:
                        md_lines.extend([
                            '### 📊 Aggregation Examples',
                            ''
                        ])
                    elif 'String field queries' in content:
                        md_lines.extend([
                            '#### 📝 String Field Operations',
                            ''
                        ])
                    elif 'Numeric field queries' in content:
                        md_lines.extend([
                            '#### 🔢 Numeric Field Operations',
                            ''
                        ])
                    elif 'Boolean field queries' in content:
                        md_lines.extend([
                            '#### ✅ Boolean Field Operations',
                            ''
                        ])
                    elif 'Date' in content and 'field queries' in content:
                        md_lines.extend([
                            '#### 📅 Date/DateTime Field Operations',
                            ''
                        ])
                    elif 'ForeignKey' in content:
                        md_lines.extend([
                            f'#### 🔗 {content}',
                            ''
                        ])
                    elif 'ManyToMany' in content:
                        md_lines.extend([
                            f'#### 🔄 {content}',
                            ''
                        ])
                    elif 'Bridge Table' in content:
                        md_lines.extend([
                            f'#### 🌉 {content}',
                            ''
                        ])
                    else:
                        md_lines.extend([
                            f'#### {content}',
                            ''
                        ])
                    continue

                # import/from lines -> highlighted inline code
                if stripped.startswith('from ') or stripped.startswith('import '):
                    close_code()
                    md_lines.extend([
                        f'**Import Required**: `{stripped}`',
                        ''
                    ])
                    continue

                # Query-like or python expressions -> enhanced code block
                if ('.objects' in stripped) or stripped.startswith('instance.') or stripped.endswith(')') or stripped.endswith(']') or ('=' in stripped and not stripped.startswith('#')):
                    if not in_code:
                        md_lines.append('```python')
                        in_code = True
                    md_lines.append(stripped)
                    continue

                # fallback plain text with better formatting
                close_code()
                if stripped:
                    md_lines.append(stripped)

            close_code()

            # Add footer
            md_lines.extend([
                '---',
                '',
                '## 📚 Additional Resources',
                '',
                '- [Django QuerySet API Reference](https://docs.djangoproject.com/en/stable/ref/models/querysets/)',
                '- [Django Model Field Reference](https://docs.djangoproject.com/en/stable/ref/models/fields/)',
                '- [Django Database Queries](https://docs.djangoproject.com/en/stable/topics/db/queries/)',
                '',
                f'*Generated on {Path.cwd().name} Django project*'
            ])

            with open(result_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(md_lines))
        except Exception:
            # best-effort raw dump
            try:
                with open(result_path, 'w', encoding='utf-8') as f:
                    for line in self._result_lines:
                        f.write(line + '\n')
            except Exception:
                pass
        finally:
            # restore original write callable
            try:
                self.stdout.write = original_stdout_write
            except Exception:
                pass

    def analyze_model(self, model, bridge_tables_analyzed):
        model_name = model.__name__
        app_name = model._meta.app_label
        
        self.stdout.write(self.style.SUCCESS(f"\n{'='*80}"))
        self.stdout.write(self.style.SUCCESS(f"MODEL: {model_name} ({app_name}.models.{model_name})"))
        self.stdout.write(self.style.SUCCESS(f"Table: {model._meta.db_table}"))
        self.stdout.write(self.style.SUCCESS(f"{'='*80}"))

        # Basic model queries
        self.stdout.write(self.style.HTTP_INFO(f"\n# Basic Model Queries"))
        self.stdout.write(f"{model_name}.objects.all()")
        self.stdout.write(f"{model_name}.objects.count()")
        self.stdout.write(f"{model_name}.objects.first()")
        self.stdout.write(f"{model_name}.objects.last()")
        self.stdout.write(f"{model_name}.objects.exists()")

        # Analyze all fields
        for field in model._meta.get_fields():
            self.analyze_field(model, field, bridge_tables_analyzed)

        # Show aggregation examples
        self.show_aggregation_examples(model)

    def analyze_field(self, model, field, bridge_tables_analyzed):
        model_name = model.__name__
        field_name = field.name

        # --- Direct Model Fields ---
        if isinstance(field, models.Field):
            field_type = field.get_internal_type()
            self.stdout.write(self.style.WARNING(f"\n# Field: '{field_name}' (Type: {field_type})"))

            if isinstance(field, models.AutoField):
                self.stdout.write(f"{model_name}.objects.get(pk=1)")
                self.stdout.write(f"{model_name}.objects.filter(pk__in=[1, 2, 3])")

            elif isinstance(field, (models.CharField, models.TextField)):
                self.stdout.write(f"# String field queries")
                self.stdout.write(f"{model_name}.objects.filter({field_name}='exact_value')")
                self.stdout.write(f"{model_name}.objects.filter({field_name}__icontains='partial')")
                self.stdout.write(f"{model_name}.objects.filter({field_name}__startswith='prefix')")
                self.stdout.write(f"{model_name}.objects.filter({field_name}__endswith='suffix')")
                self.stdout.write(f"{model_name}.objects.filter({field_name}__isnull=False)")
                self.stdout.write(f"{model_name}.objects.filter({field_name}__regex=r'^[A-Z]')")

            elif isinstance(field, (models.IntegerField, models.FloatField, models.DecimalField)):
                self.stdout.write(f"# Numeric field queries")
                self.stdout.write(f"{model_name}.objects.filter({field_name}=100)")
                self.stdout.write(f"{model_name}.objects.filter({field_name}__gt=100)")
                self.stdout.write(f"{model_name}.objects.filter({field_name}__gte=100)")
                self.stdout.write(f"{model_name}.objects.filter({field_name}__lt=200)")
                self.stdout.write(f"{model_name}.objects.filter({field_name}__lte=200)")
                self.stdout.write(f"{model_name}.objects.filter({field_name}__range=(50, 150))")
                self.stdout.write(f"{model_name}.objects.filter({field_name}__in=[10, 20, 30])")

            elif isinstance(field, models.BooleanField):
                self.stdout.write(f"# Boolean field queries")
                self.stdout.write(f"{model_name}.objects.filter({field_name}=True)")
                self.stdout.write(f"{model_name}.objects.filter({field_name}=False)")

            elif isinstance(field, (models.DateField, models.DateTimeField)):
                self.stdout.write(f"# Date/DateTime field queries")
                self.stdout.write(f"from django.utils import timezone")
                self.stdout.write(f"from datetime import date, datetime")
                self.stdout.write(f"{model_name}.objects.filter({field_name}__year=2025)")
                self.stdout.write(f"{model_name}.objects.filter({field_name}__month=1)")
                self.stdout.write(f"{model_name}.objects.filter({field_name}__day=15)")
                self.stdout.write(f"{model_name}.objects.filter({field_name}__lt=timezone.now())")
                self.stdout.write(f"{model_name}.objects.filter({field_name}__date=date.today())")

            elif isinstance(field, models.ForeignKey):
                self.analyze_foreign_key_field(model, field)

            elif isinstance(field, models.ManyToManyField):
                self.analyze_manytomany_field(model, field, bridge_tables_analyzed)

        # --- Reverse Relationships ---
        elif isinstance(field, (ManyToOneRel, ManyToManyRel, OneToOneRel)):
            self.analyze_reverse_relationship(model, field)

    def analyze_foreign_key_field(self, model, field):
        model_name = model.__name__
        field_name = field.name
        related_model = field.related_model
        related_model_name = related_model.__name__
        
        self.stdout.write(f"# ForeignKey to {related_model_name}")
        
        # Basic FK queries
        self.stdout.write(f"# Basic ForeignKey queries")
        self.stdout.write(f"{model_name}.objects.filter({field_name}_id=1)")
        self.stdout.write(f"{model_name}.objects.filter({field_name}__isnull=False)")
        self.stdout.write(f"{model_name}.objects.filter({field_name}__isnull=True)")
        self.stdout.write(f"{model_name}.objects.select_related('{field_name}')")
        
        # Get all fields from the related model for relationship filtering
        related_fields = self.get_model_fields_info(related_model)
        
        if related_fields:
            self.stdout.write(f"# Filter through {related_model_name} fields:")
            
            for rel_field_name, rel_field_type, rel_field_obj in related_fields:
                lookup_prefix = f"{field_name}__{rel_field_name}"
                
                if rel_field_type == 'AutoField':
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}=1)")
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}__in=[1, 2, 3])")
                    
                elif rel_field_type in ['CharField', 'TextField']:
                    self.stdout.write(f"# String field in {related_model_name}")
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}='exact_value')")
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}__icontains='partial')")
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}__startswith='prefix')")
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}__endswith='suffix')")
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}__isnull=False)")
                    
                elif rel_field_type in ['IntegerField', 'FloatField', 'DecimalField']:
                    self.stdout.write(f"# Numeric field in {related_model_name}")
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}=100)")
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}__gt=100)")
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}__lt=200)")
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}__range=(50, 150))")
                    
                elif rel_field_type == 'BooleanField':
                    self.stdout.write(f"# Boolean field in {related_model_name}")
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}=True)")
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}=False)")
                    
                elif rel_field_type in ['DateField', 'DateTimeField']:
                    self.stdout.write(f"# Date field in {related_model_name}")
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}__year=2025)")
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}__month=1)")
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}__lt=timezone.now())")
                    
                elif rel_field_type == 'ForeignKey':
                    # Nested FK relationship
                    nested_related_model = rel_field_obj.related_model.__name__
                    self.stdout.write(f"# Nested ForeignKey to {nested_related_model} through {related_model_name}")
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}_id=1)")
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}__isnull=False)")
                    
                    # Show one level deeper for nested relationships
                    nested_fields = self.get_model_fields_info(rel_field_obj.related_model, max_depth=1)
                    for nested_field_name, nested_field_type, _ in nested_fields[:3]:  # Limit to first 3 fields
                        nested_lookup = f"{lookup_prefix}__{nested_field_name}"
                        if nested_field_type in ['CharField', 'TextField']:
                            self.stdout.write(f"{model_name}.objects.filter({nested_lookup}__icontains='value')")
                        elif nested_field_type in ['IntegerField', 'FloatField', 'DecimalField']:
                            self.stdout.write(f"{model_name}.objects.filter({nested_lookup}__gt=100)")
                            
        # Complex FK queries
        self.stdout.write(f"# Complex ForeignKey queries")
        self.stdout.write(f"# Multiple conditions on related model")
        self.stdout.write(f"from django.db.models import Q")
        self.stdout.write(f"{model_name}.objects.filter(")
        self.stdout.write(f"    Q({field_name}__field1='value1') & Q({field_name}__field2='value2')")
        self.stdout.write(f")")
        
        # Exclude queries
        self.stdout.write(f"# Exclude queries")
        self.stdout.write(f"{model_name}.objects.exclude({field_name}__isnull=True)")
        self.stdout.write(f"{model_name}.objects.exclude({field_name}__some_field='unwanted_value')")
        
        # Aggregation through FK
        self.stdout.write(f"# Aggregation through ForeignKey")
        self.stdout.write(f"from django.db.models import Count")
        self.stdout.write(f"{model_name}.objects.values('{field_name}__some_field').annotate(count=Count('id'))")
        
        # Ordering through FK
        self.stdout.write(f"# Ordering through ForeignKey")
        self.stdout.write(f"{model_name}.objects.order_by('{field_name}__some_field')")
        self.stdout.write(f"{model_name}.objects.order_by('-{field_name}__some_field')")

    def get_model_fields_info(self, model, max_depth=0):
        """Get information about model fields for relationship filtering"""
        fields_info = []
        
        for field in model._meta.get_fields():
            if isinstance(field, models.Field):
                field_type = field.get_internal_type()
                fields_info.append((field.name, field_type, field))
                
                # For nested FK relationships (limited depth to avoid infinite recursion)
                if max_depth > 0 and isinstance(field, models.ForeignKey):
                    try:
                        # Add some nested fields but limit to avoid overwhelming output
                        nested_fields = self.get_model_fields_info(field.related_model, max_depth - 1)
                        # Only add first few nested fields to keep output manageable
                        for nested_field in nested_fields[:2]:
                            nested_name = f"{field.name}__{nested_field[0]}"
                            fields_info.append((nested_name, nested_field[1], nested_field[2]))
                    except:
                        # Skip if there are issues with nested relationships
                        pass
        
        return fields_info

    def analyze_manytomany_field(self, model, field, bridge_tables_analyzed):
        model_name = model.__name__
        field_name = field.name
        related_model = field.related_model
        related_model_name = related_model.__name__
        through_model = field.remote_field.through

        self.stdout.write(f"# ManyToMany field to {related_model_name}")
        
        # Basic M2M queries
        self.stdout.write(f"# Basic ManyToMany queries")
        self.stdout.write(f"{model_name}.objects.filter({field_name}__isnull=False)")
        self.stdout.write(f"{model_name}.objects.filter({field_name}__id=1)")
        self.stdout.write(f"{model_name}.objects.prefetch_related('{field_name}')")
        
        # Filter through related model fields
        related_fields = self.get_model_fields_info(related_model)
        if related_fields:
            self.stdout.write(f"# Filter through {related_model_name} fields:")
            for rel_field_name, rel_field_type, _ in related_fields[:5]:  # Limit to first 5 fields
                lookup_prefix = f"{field_name}__{rel_field_name}"
                if rel_field_type in ['CharField', 'TextField']:
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}__icontains='value')")
                elif rel_field_type in ['IntegerField', 'FloatField', 'DecimalField']:
                    self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}__gt=100)")
        
        # Check if it's a custom through model (bridge table)
        if not through_model._meta.auto_created:
            through_model_name = through_model.__name__
            through_app_name = through_model._meta.app_label
            bridge_key = f"{through_app_name}.{through_model_name}"
            
            self.stdout.write(self.style.HTTP_INFO(f"# Custom Bridge Table: {through_model_name}"))
            self.stdout.write(f"# Table: {through_model._meta.db_table}")
            
            # Bridge table specific queries
            self.stdout.write(f"# Query through bridge table fields")
            bridge_fields = self.get_model_fields_info(through_model)
            for bridge_field_name, bridge_field_type, bridge_field_obj in bridge_fields:
                if not isinstance(bridge_field_obj, models.ForeignKey):
                    lookup_prefix = f"{field_name}__{bridge_field_name}"
                    if bridge_field_type in ['CharField', 'TextField']:
                        self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}__icontains='value')")
                    elif bridge_field_type in ['IntegerField', 'FloatField', 'DecimalField']:
                        self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}__gt=100)")
                    elif bridge_field_type in ['DateField', 'DateTimeField']:
                        self.stdout.write(f"{model_name}.objects.filter({lookup_prefix}__year=2025)")
            
            # Analyze bridge table separately if not already done
            if bridge_key not in bridge_tables_analyzed:
                bridge_tables_analyzed.add(bridge_key)
                self.stdout.write(self.style.SQL_KEYWORD(f"\n# Bridge Table Analysis: {through_model_name}"))
                self.analyze_bridge_table(through_model)

        # Instance-level M2M operations
        self.stdout.write(f"# Instance-level ManyToMany operations")
        self.stdout.write(f"instance = {model_name}.objects.get(pk=1)")
        self.stdout.write(f"instance.{field_name}.all()")
        self.stdout.write(f"instance.{field_name}.count()")
        self.stdout.write(f"instance.{field_name}.filter(some_field='value')")
        self.stdout.write(f"instance.{field_name}.add({related_model_name.lower()}_instance)")
        self.stdout.write(f"instance.{field_name}.remove({related_model_name.lower()}_instance)")
        self.stdout.write(f"instance.{field_name}.clear()")

    def analyze_bridge_table(self, through_model):
        bridge_name = through_model.__name__
        self.stdout.write(f"# Direct queries on bridge table {bridge_name}")
        self.stdout.write(f"{bridge_name}.objects.all()")
        self.stdout.write(f"{bridge_name}.objects.select_related()")
        
        # Show all fields in the bridge table with relationship filtering
        for field in through_model._meta.get_fields():
            if isinstance(field, models.Field):
                field_name = field.name
                if isinstance(field, models.ForeignKey):
                    related_model = field.related_model
                    related_model_name = related_model.__name__
                    self.stdout.write(f"# ForeignKey to {related_model_name} in bridge table")
                    self.stdout.write(f"{bridge_name}.objects.filter({field_name}__id=1)")
                    
                    # Show filtering through FK fields in bridge table
                    related_fields = self.get_model_fields_info(related_model)
                    for rel_field_name, rel_field_type, _ in related_fields[:3]:  # Limit output
                        lookup_prefix = f"{field_name}__{rel_field_name}"
                        if rel_field_type in ['CharField', 'TextField']:
                            self.stdout.write(f"{bridge_name}.objects.filter({lookup_prefix}__icontains='value')")
                        elif rel_field_type in ['IntegerField', 'FloatField', 'DecimalField']:
                            self.stdout.write(f"{bridge_name}.objects.filter({lookup_prefix}__gt=100)")
                else:
                    self.stdout.write(f"# Field: {field_name}")
                    self.stdout.write(f"{bridge_name}.objects.filter({field_name}='value')")

    def analyze_reverse_relationship(self, model, field):
        model_name = model.__name__
        field_name = field.name
        related_model = field.related_model.__name__
        
        if isinstance(field, ManyToOneRel):
            rel_type = "One-to-Many (Reverse ForeignKey)"
        elif isinstance(field, ManyToManyRel):
            rel_type = "Many-to-Many (Reverse)"
        else:
            rel_type = "One-to-One (Reverse)"
            
        self.stdout.write(self.style.WARNING(f"\n# Reverse Relation: {rel_type} from {related_model}"))
        self.stdout.write(f"# Access from {model_name} instance")
        self.stdout.write(f"instance = {model_name}.objects.get(pk=1)")
        self.stdout.write(f"instance.{field_name}.all()")
        self.stdout.write(f"instance.{field_name}.count()")
        self.stdout.write(f"instance.{field_name}.filter(some_field='value')")
        
        # Query from the related model side with relationship filtering
        self.stdout.write(f"# Query from {related_model} side")
        if isinstance(field, ManyToOneRel):
            # ForeignKey reverse
            fk_field = field.remote_field.name
            self.stdout.write(f"{related_model}.objects.filter({fk_field}__id=1)")
            
            # Show filtering through reverse FK relationship
            model_fields = self.get_model_fields_info(model)
            for model_field_name, model_field_type, _ in model_fields[:3]:  # Limit output
                lookup_prefix = f"{fk_field}__{model_field_name}"
                if model_field_type in ['CharField', 'TextField']:
                    self.stdout.write(f"{related_model}.objects.filter({lookup_prefix}__icontains='value')")
                elif model_field_type in ['IntegerField', 'FloatField', 'DecimalField']:
                    self.stdout.write(f"{related_model}.objects.filter({lookup_prefix}__gt=100)")
                    
        elif isinstance(field, ManyToManyRel):
            # M2M reverse
            m2m_field = field.remote_field.name
            self.stdout.write(f"{related_model}.objects.filter({m2m_field}__id=1)")
            
            # Show filtering through reverse M2M relationship
            model_fields = self.get_model_fields_info(model)
            for model_field_name, model_field_type, _ in model_fields[:3]:  # Limit output
                lookup_prefix = f"{m2m_field}__{model_field_name}"
                if model_field_type in ['CharField', 'TextField']:
                    self.stdout.write(f"{related_model}.objects.filter({lookup_prefix}__icontains='value')")
                elif model_field_type in ['IntegerField', 'FloatField', 'DecimalField']:
                    self.stdout.write(f"{related_model}.objects.filter({lookup_prefix}__gt=100)")

    def show_aggregation_examples(self, model):
        model_name = model.__name__
        self.stdout.write(self.style.HTTP_INFO(f"\n# Aggregation Examples for {model_name}"))
        self.stdout.write(f"from django.db.models import Count, Sum, Avg, Max, Min")
        self.stdout.write(f"{model_name}.objects.aggregate(total=Count('id'))")
        
        # Find numeric fields for aggregation examples
        numeric_fields = []
        fk_fields = []
        for field in model._meta.get_fields():
            if isinstance(field, (models.IntegerField, models.FloatField, models.DecimalField)):
                numeric_fields.append(field.name)
            elif isinstance(field, models.ForeignKey):
                fk_fields.append(field.name)
        
        if numeric_fields:
            field_name = numeric_fields[0]
            self.stdout.write(f"{model_name}.objects.aggregate(avg_{field_name}=Avg('{field_name}'))")
            self.stdout.write(f"{model_name}.objects.aggregate(sum_{field_name}=Sum('{field_name}'))")
        
        # Annotation examples with FK relationships
        self.stdout.write(f"# Annotation examples")
        if fk_fields:
            fk_field = fk_fields[0]
            self.stdout.write(f"{model_name}.objects.annotate(related_count=Count('{fk_field}'))")
            self.stdout.write(f"{model_name}.objects.values('{fk_field}__some_field').annotate(count=Count('id'))")
        
        self.stdout.write(f"\n# Advanced queries")
        self.stdout.write(f"{model_name}.objects.distinct()")
        self.stdout.write(f"{model_name}.objects.order_by('id')")
        self.stdout.write(f"{model_name}.objects.order_by('-id')  # Descending")
        self.stdout.write(f"{model_name}.objects.values('field1', 'field2')")
        self.stdout.write(f"{model_name}.objects.values_list('field1', flat=True)")
        
        # Advanced FK queries
        if fk_fields:
            self.stdout.write(f"# Advanced ForeignKey queries")
            fk_field = fk_fields[0]
            self.stdout.write(f"{model_name}.objects.select_related('{fk_field}').order_by('{fk_field}__some_field')")
            self.stdout.write(f"{model_name}.objects.prefetch_related('{fk_field}')")