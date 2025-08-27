# In your_app/management/commands/crud_queries.py

from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import models
from django.db.models.fields.reverse_related import ManyToManyRel, ManyToOneRel, OneToOneRel
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Generates comprehensive CRUD queries for Django models and outputs to beautiful markdown.'

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
        parser.add_argument(
            '--output-file', 
            type=str, 
            default='django_crud_queries.md',
            help='Output markdown file name (default: django_crud_queries.md)'
        )

    def handle(self, *args, **kwargs):
        app_name = kwargs.get('app')
        model_name = kwargs.get('model')
        include_django = kwargs.get('include_django', False)
        output_file = kwargs.get('output_file')

        if model_name and not app_name:
            self.stdout.write(self.style.ERROR("Error: --model requires --app to be specified."))
            return

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
            return

        # Generate markdown content
        markdown_content = self.generate_markdown_content(models_to_analyze)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        self.stdout.write(
            self.style.SUCCESS(f"CRUD queries documentation generated: {output_file}")
        )

    def generate_markdown_content(self, models_to_analyze):
        content = []
        
        # Header
        content.append("# Django CRUD Queries Documentation")
        content.append(f"\n*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        content.append(f"\n*Total Models Analyzed: {len(models_to_analyze)}*")
        
        # Table of Contents
        content.append("\n## Table of Contents")
        for model in models_to_analyze:
            model_name = model.__name__
            app_name = model._meta.app_label
            content.append(f"- [{model_name}](#{model_name.lower()}-{app_name})")
        
        # Track bridge tables
        bridge_tables_analyzed = set()
        
        # Generate content for each model
        for model in models_to_analyze:
            content.extend(self.generate_model_documentation(model, bridge_tables_analyzed))
        
        return "\n".join(content)

    def generate_model_documentation(self, model, bridge_tables_analyzed):
        model_name = model.__name__
        app_name = model._meta.app_label
        content = []
        
        # Model Header
        content.append(f"\n---\n")
        content.append(f"## {model_name} ({app_name})")
        content.append(f"\n**Database Table:** `{model._meta.db_table}`")
        
        # Model Fields Overview
        content.extend(self.generate_fields_overview(model))
        
        # Basic CRUD Operations
        content.extend(self.generate_basic_crud(model))
        
        # Field-specific queries
        content.extend(self.generate_field_queries(model, bridge_tables_analyzed))
        
        # Data Display Examples
        content.extend(self.generate_data_display_examples(model))
        
        return content

    def generate_fields_overview(self, model):
        content = []
        content.append(f"\n### 📋 Model Fields Overview")
        content.append("\n| Field Name | Type | Properties | Description |")
        content.append("|------------|------|------------|-------------|")
        
        for field in model._meta.get_fields():
            field_name = field.name
            properties = []
            description = ""
            
            if isinstance(field, models.Field):
                field_type = field.get_internal_type()
                
                # Collect field properties
                if getattr(field, 'null', False):
                    properties.append('`null=True`')
                if getattr(field, 'blank', False):
                    properties.append('`blank=True`')
                if getattr(field, 'unique', False):
                    properties.append('`unique=True`')
                if getattr(field, 'db_index', False):
                    properties.append('`db_index=True`')
                if hasattr(field, 'max_length') and field.max_length:
                    properties.append(f'`max_length={field.max_length}`')
                
                if isinstance(field, models.ForeignKey):
                    description = f"References `{field.related_model.__name__}`"
                elif isinstance(field, models.ManyToManyField):
                    description = f"Many-to-Many with `{field.related_model.__name__}`"
                    
            elif isinstance(field, (ManyToOneRel, ManyToManyRel, OneToOneRel)):
                if isinstance(field, ManyToOneRel):
                    field_type = "Reverse ForeignKey"
                    description = f"Reverse relation from `{field.related_model.__name__}`"
                elif isinstance(field, ManyToManyRel):
                    field_type = "Reverse ManyToMany"
                    description = f"Reverse M2M from `{field.related_model.__name__}`"
                else:
                    field_type = "Reverse OneToOne"
                    description = f"Reverse O2O from `{field.related_model.__name__}`"
            
            props_str = ', '.join(properties) if properties else '-'
            content.append(f"| `{field_name}` | {field_type} | {props_str} | {description} |")
        
        return content

    def generate_basic_crud(self, model):
        model_name = model.__name__
        content = []
        
        content.append(f"\n### 🔧 Basic CRUD Operations")
        
        # CREATE
        content.append(f"\n#### ➕ Create Operations")
        content.append("```python")
        content.append(f"# Create a new {model_name}")
        content.append(f"{model_name.lower()} = {model_name}.objects.create(")
        content.append("    field1='value1',")
        content.append("    field2='value2',")
        content.append("    # ... other fields")
        content.append(")")
        content.append("")
        content.append(f"# Alternative: Create and save")
        content.append(f"{model_name.lower()} = {model_name}(")
        content.append("    field1='value1',")
        content.append("    field2='value2'")
        content.append(")")
        content.append(f"{model_name.lower()}.save()")
        content.append("")
        content.append(f"# Bulk create")
        content.append(f"{model_name}.objects.bulk_create([")
        content.append(f"    {model_name}(field1='value1'),")
        content.append(f"    {model_name}(field1='value2'),")
        content.append(f"    {model_name}(field1='value3'),")
        content.append("])")
        content.append("```")
        
        # READ
        content.append(f"\n#### 📖 Read Operations")
        content.append("```python")
        content.append(f"# Get all {model_name} objects")
        content.append(f"all_{model_name.lower()}s = {model_name}.objects.all()")
        content.append("")
        content.append(f"# Get single object")
        content.append(f"{model_name.lower()} = {model_name}.objects.get(pk=1)")
        content.append(f"{model_name.lower()} = {model_name}.objects.get(field='value')")
        content.append("")
        content.append(f"# Get or create")
        content.append(f"{model_name.lower()}, created = {model_name}.objects.get_or_create(")
        content.append("    field='value',")
        content.append("    defaults={'other_field': 'default_value'}")
        content.append(")")
        content.append("")
        content.append(f"# Filter operations")
        content.append(f"filtered = {model_name}.objects.filter(field='value')")
        content.append(f"excluded = {model_name}.objects.exclude(field='unwanted')")
        content.append("")
        content.append(f"# First, last, exists")
        content.append(f"first = {model_name}.objects.first()")
        content.append(f"last = {model_name}.objects.last()")
        content.append(f"exists = {model_name}.objects.filter(field='value').exists()")
        content.append("")
        content.append(f"# Count")
        content.append(f"count = {model_name}.objects.count()")
        content.append(f"filtered_count = {model_name}.objects.filter(field='value').count()")
        content.append("```")
        
        # UPDATE
        content.append(f"\n#### ✏️ Update Operations")
        content.append("```python")
        content.append(f"# Update single object")
        content.append(f"{model_name.lower()} = {model_name}.objects.get(pk=1)")
        content.append(f"{model_name.lower()}.field = 'new_value'")
        content.append(f"{model_name.lower()}.save()")
        content.append("")
        content.append(f"# Update specific fields only")
        content.append(f"{model_name.lower()}.save(update_fields=['field1', 'field2'])")
        content.append("")
        content.append(f"# Bulk update")
        content.append(f"{model_name}.objects.filter(condition=True).update(")
        content.append("    field1='new_value1',")
        content.append("    field2='new_value2'")
        content.append(")")
        content.append("")
        content.append(f"# Update or create")
        content.append(f"{model_name.lower()}, created = {model_name}.objects.update_or_create(")
        content.append("    field='lookup_value',")
        content.append("    defaults={'other_field': 'updated_value'}")
        content.append(")")
        content.append("```")
        
        # DELETE
        content.append(f"\n#### 🗑️ Delete Operations")
        content.append("```python")
        content.append(f"# Delete single object")
        content.append(f"{model_name.lower()} = {model_name}.objects.get(pk=1)")
        content.append(f"{model_name.lower()}.delete()")
        content.append("")
        content.append(f"# Bulk delete")
        content.append(f"{model_name}.objects.filter(condition=True).delete()")
        content.append("")
        content.append(f"# Delete all (be careful!)")
        content.append(f"{model_name}.objects.all().delete()")
        content.append("```")
        
        return content

    def generate_field_queries(self, model, bridge_tables_analyzed):
        content = []
        content.append(f"\n### 🔍 Field-Specific Queries")
        
        for field in model._meta.get_fields():
            if isinstance(field, models.Field):
                content.extend(self.generate_field_specific_queries(model, field, bridge_tables_analyzed))
        
        # Reverse relationships
        content.append(f"\n#### 🔄 Reverse Relationship Queries")
        for field in model._meta.get_fields():
            if isinstance(field, (ManyToOneRel, ManyToManyRel, OneToOneRel)):
                content.extend(self.generate_reverse_relationship_queries(model, field))
        
        return content

    def generate_field_specific_queries(self, model, field, bridge_tables_analyzed):
        model_name = model.__name__
        field_name = field.name
        field_type = field.get_internal_type()
        content = []
        
        content.append(f"\n##### 🏷️ {field_name} ({field_type})")
        content.append("```python")
        
        if isinstance(field, models.AutoField):
            content.append(f"# Primary key queries")
            content.append(f"{model_name}.objects.get(pk=1)")
            content.append(f"{model_name}.objects.filter(pk__in=[1, 2, 3])")
            content.append(f"{model_name}.objects.filter(pk__gt=10)")
            
        elif isinstance(field, (models.CharField, models.TextField)):
            content.append(f"# String field queries")
            content.append(f"{model_name}.objects.filter({field_name}='exact_match')")
            content.append(f"{model_name}.objects.filter({field_name}__icontains='partial')")
            content.append(f"{model_name}.objects.filter({field_name}__startswith='prefix')")
            content.append(f"{model_name}.objects.filter({field_name}__endswith='suffix')")
            content.append(f"{model_name}.objects.filter({field_name}__isnull=False)")
            content.append(f"{model_name}.objects.filter({field_name}__regex=r'^[A-Z]')")
            content.append(f"{model_name}.objects.filter({field_name}__in=['val1', 'val2'])")
            
        elif isinstance(field, (models.IntegerField, models.FloatField, models.DecimalField)):
            content.append(f"# Numeric field queries")
            content.append(f"{model_name}.objects.filter({field_name}=100)")
            content.append(f"{model_name}.objects.filter({field_name}__gt=100)")
            content.append(f"{model_name}.objects.filter({field_name}__gte=100)")
            content.append(f"{model_name}.objects.filter({field_name}__lt=200)")
            content.append(f"{model_name}.objects.filter({field_name}__lte=200)")
            content.append(f"{model_name}.objects.filter({field_name}__range=(50, 150))")
            content.append(f"{model_name}.objects.filter({field_name}__in=[10, 20, 30])")
            
        elif isinstance(field, models.BooleanField):
            content.append(f"# Boolean field queries")
            content.append(f"{model_name}.objects.filter({field_name}=True)")
            content.append(f"{model_name}.objects.filter({field_name}=False)")
            
        elif isinstance(field, (models.DateField, models.DateTimeField)):
            content.append(f"# Date/DateTime field queries")
            content.append(f"from django.utils import timezone")
            content.append(f"from datetime import date, datetime")
            content.append(f"{model_name}.objects.filter({field_name}__year=2025)")
            content.append(f"{model_name}.objects.filter({field_name}__month=1)")
            content.append(f"{model_name}.objects.filter({field_name}__day=15)")
            content.append(f"{model_name}.objects.filter({field_name}__lt=timezone.now())")
            content.append(f"{model_name}.objects.filter({field_name}__date=date.today())")
            content.append(f"{model_name}.objects.filter({field_name}__range=(start_date, end_date))")
            
        elif isinstance(field, models.ForeignKey):
            content.extend(self.generate_foreign_key_queries(model, field))
            
        elif isinstance(field, models.ManyToManyField):
            content.extend(self.generate_manytomany_queries(model, field, bridge_tables_analyzed))
        
        content.append("```")
        return content

    def generate_foreign_key_queries(self, model, field):
        model_name = model.__name__
        field_name = field.name
        related_model_name = field.related_model.__name__
        content = []
        
        content.append(f"# ForeignKey to {related_model_name}")
        content.append(f"{model_name}.objects.filter({field_name}_id=1)")
        content.append(f"{model_name}.objects.filter({field_name}__isnull=False)")
        content.append(f"{model_name}.objects.select_related('{field_name}')")
        content.append("")
        content.append(f"# Filter through related model fields")
        content.append(f"{model_name}.objects.filter({field_name}__some_field='value')")
        content.append(f"{model_name}.objects.filter({field_name}__name__icontains='search')")
        content.append(f"{model_name}.objects.filter({field_name}__created_at__year=2025)")
        content.append("")
        content.append(f"# Complex FK queries")
        content.append(f"from django.db.models import Q")
        content.append(f"{model_name}.objects.filter(")
        content.append(f"    Q({field_name}__field1='value1') & Q({field_name}__field2='value2')")
        content.append(f")")
        content.append("")
        content.append(f"# Ordering through FK")
        content.append(f"{model_name}.objects.order_by('{field_name}__name')")
        content.append(f"{model_name}.objects.order_by('-{field_name}__created_at')")
        
        return content

    def generate_manytomany_queries(self, model, field, bridge_tables_analyzed):
        model_name = model.__name__
        field_name = field.name
        related_model_name = field.related_model.__name__
        through_model = field.remote_field.through
        content = []
        
        content.append(f"# ManyToMany with {related_model_name}")
        content.append(f"{model_name}.objects.filter({field_name}__isnull=False)")
        content.append(f"{model_name}.objects.filter({field_name}__id=1)")
        content.append(f"{model_name}.objects.prefetch_related('{field_name}')")
        content.append("")
        content.append(f"# Filter through related model")
        content.append(f"{model_name}.objects.filter({field_name}__name='value')")
        content.append(f"{model_name}.objects.filter({field_name}__is_active=True)")
        content.append("")
        content.append(f"# Instance-level M2M operations")
        content.append(f"instance = {model_name}.objects.get(pk=1)")
        content.append(f"instance.{field_name}.all()")
        content.append(f"instance.{field_name}.count()")
        content.append(f"instance.{field_name}.filter(name='value')")
        content.append(f"instance.{field_name}.add({related_model_name.lower()}_instance)")
        content.append(f"instance.{field_name}.remove({related_model_name.lower()}_instance)")
        content.append(f"instance.{field_name}.clear()")
        
        # Bridge table analysis
        if not through_model._meta.auto_created:
            through_model_name = through_model.__name__
            bridge_key = f"{through_model._meta.app_label}.{through_model_name}"
            
            content.append("")
            content.append(f"# Custom Bridge Table: {through_model_name}")
            content.append(f"# Direct queries on bridge table")
            content.append(f"{through_model_name}.objects.all()")
            content.append(f"{through_model_name}.objects.filter(custom_field='value')")
            content.append(f"{through_model_name}.objects.select_related()")
            
            if bridge_key not in bridge_tables_analyzed:
                bridge_tables_analyzed.add(bridge_key)
        
        return content

    def generate_reverse_relationship_queries(self, model, field):
        model_name = model.__name__
        field_name = field.name
        related_model_name = field.related_model.__name__
        content = []
        
        if isinstance(field, ManyToOneRel):
            rel_type = "One-to-Many (Reverse FK)"
        elif isinstance(field, ManyToManyRel):
            rel_type = "Many-to-Many (Reverse)"
        else:
            rel_type = "One-to-One (Reverse)"
        
        content.append(f"\n##### 🔄 {field_name} ({rel_type} from {related_model_name})")
        content.append("```python")
        content.append(f"# Access from {model_name} instance")
        content.append(f"instance = {model_name}.objects.get(pk=1)")
        content.append(f"instance.{field_name}.all()")
        content.append(f"instance.{field_name}.count()")
        content.append(f"instance.{field_name}.filter(some_field='value')")
        content.append("")
        content.append(f"# Query from {related_model_name} side")
        if isinstance(field, ManyToOneRel):
            fk_field = field.remote_field.name
            content.append(f"{related_model_name}.objects.filter({fk_field}__id=1)")
            content.append(f"{related_model_name}.objects.filter({fk_field}__some_field='value')")
        elif isinstance(field, ManyToManyRel):
            m2m_field = field.remote_field.name
            content.append(f"{related_model_name}.objects.filter({m2m_field}__id=1)")
            content.append(f"{related_model_name}.objects.filter({m2m_field}__some_field='value')")
        content.append("```")
        
        return content

    def generate_data_display_examples(self, model):
        model_name = model.__name__
        content = []
        
        content.append(f"\n### 📊 Data Display & Output Examples")
        
        # Basic display
        content.append(f"\n#### 🖨️ Basic Data Display")
        content.append("```python")
        content.append(f"# Print all objects")
        content.append(f"for obj in {model_name}.objects.all():")
        content.append(f"    print(obj)")
        content.append("")
        content.append(f"# Print specific fields")
        content.append(f"for obj in {model_name}.objects.all():")
        content.append(f"    print(f'ID: {{obj.id}}, Field: {{obj.some_field}}')")
        content.append("```")
        
        # Values and values_list
        content.append(f"\n#### 📋 Values & Values List")
        content.append("```python")
        content.append(f"# Get dictionaries")
        content.append(f"data = {model_name}.objects.values('field1', 'field2')")
        content.append(f"for item in data:")
        content.append(f"    print(item)  # {{'field1': 'value1', 'field2': 'value2'}}")
        content.append("")
        content.append(f"# Get tuples")
        content.append(f"data = {model_name}.objects.values_list('field1', 'field2')")
        content.append(f"for item in data:")
        content.append(f"    print(item)  # ('value1', 'value2')")
        content.append("")
        content.append(f"# Get flat list")
        content.append(f"names = {model_name}.objects.values_list('name', flat=True)")
        content.append(f"print(list(names))  # ['name1', 'name2', 'name3']")
        content.append("```")
        
        # JSON output
        content.append(f"\n#### 🔄 JSON Serialization")
        content.append("```python")
        content.append(f"import json")
        content.append(f"from django.core import serializers")
        content.append("")
        content.append(f"# Django serializer")
        content.append(f"data = serializers.serialize('json', {model_name}.objects.all())")
        content.append(f"print(data)")
        content.append("")
        content.append(f"# Manual JSON with values()")
        content.append(f"data = list({model_name}.objects.values())")
        content.append(f"json_data = json.dumps(data, indent=2, default=str)")
        content.append(f"print(json_data)")
        content.append("```")
        
        # Debugging
        content.append(f"\n#### 🐛 Debugging Queries")
        content.append("```python")
        content.append(f"# Print SQL query")
        content.append(f"queryset = {model_name}.objects.filter(some_field='value')")
        content.append(f"print('SQL:', queryset.query)")
        content.append("")
        content.append(f"# Count queries executed")
        content.append(f"from django.db import connection")
        content.append(f"connection.queries_log.clear()")
        content.append(f"list({model_name}.objects.all())  # Execute query")
        content.append(f"print(f'Queries executed: {{len(connection.queries)}}')")
        content.append("```")
        
        return content