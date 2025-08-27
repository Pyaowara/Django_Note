# In your_app/management/commands/aggregate_queries.py

from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import models
from django.db.models.fields.reverse_related import ManyToManyRel, ManyToOneRel, OneToOneRel
from pathlib import Path
import re
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Generates comprehensive aggregation and annotation queries for Django models and outputs to beautiful markdown.'

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
            default='django_aggregate_queries.md',
            help='Output markdown file name (default: django_aggregate_queries.md)'
        )

    def handle(self, *args, **kwargs):
        app_name = kwargs.get('app')
        model_name = kwargs.get('model')
        include_django = kwargs.get('include_django', False)
        output_file = kwargs.get('output_file')

        # Prepare markdown output collection
        result_path = Path.cwd() / 'aggann.md'
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

        try:
            if model_name and not app_name:
                self.stdout.write("Error: --model requires --app to be specified.")
                return

            # Get all models or filter by app/model
            if app_name and model_name:
                try:
                    model = apps.get_model(app_name, model_name.capitalize())
                    models_to_analyze = [model]
                except LookupError:
                    self.stdout.write(f"Error: Model '{model_name}' not found in app '{app_name}'.")
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
                self.stdout.write("No models found to analyze.")
                return

            # Generate markdown content
            markdown_content = self.generate_markdown_content(models_to_analyze)
            
            # Write directly to buffer
            for line in markdown_content.split('\n'):
                self.stdout.write(line)
                
        finally:
            # Post-process buffer into beautiful Markdown and write file
            try:
                ansi_re = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
                cleaned = [ansi_re.sub('', line) for line in self._result_lines]

                # Write to result.md with minimal processing
                with open(result_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(cleaned))
                    
            except Exception as e:
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
                    self.stdout.write(
                        self.style.SUCCESS(f"Aggregation queries documentation generated: aggann.md")
                    )
                except Exception:
                    pass

    def generate_markdown_content(self, models_to_analyze):
        content = []
        
        # Header
        content.append("# Django Aggregation & Annotation Queries Documentation")
        content.append(f"\n*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        content.append(f"\n*Total Models Analyzed: {len(models_to_analyze)}*")
        
        # Introduction
        content.append("\n## 📖 Introduction")
        content.append("\nThis documentation covers all possible aggregation and annotation functions available in Django ORM.")
        content.append("Aggregations compute summary values over a set of objects, while annotations add calculated fields to each object in a QuerySet.")
        
        # Import statements
        content.append("\n## 📦 Required Imports")
        content.append("```python")
        content.append("from django.db.models import (")
        content.append("    Count, Sum, Avg, Max, Min, StdDev, Variance,")
        content.append("    Q, F, Case, When, Value, Exists, OuterRef, Subquery,")
        content.append("    IntegerField, CharField, BooleanField, DateTimeField")
        content.append(")")
        content.append("from django.db.models.functions import (")
        content.append("    Coalesce, Concat, Upper, Lower, Length, Substr,")
        content.append("    Extract, TruncYear, TruncMonth, TruncDay,")
        content.append("    Cast, Greatest, Least, Now, Random")
        content.append(")")
        content.append("from django.db.models import Window")
        content.append("from django.db.models.functions import RowNumber, Rank, DenseRank, Lag, Lead")
        content.append("```")
        
        # Table of Contents
        content.append("\n## 📑 Table of Contents")
        content.append("- [Basic Aggregation Functions](#basic-aggregation-functions)")
        content.append("- [Annotation Functions](#annotation-functions)")
        content.append("- [String Functions](#string-functions)")
        content.append("- [Date/Time Functions](#datetime-functions)")
        content.append("- [Conditional Expressions](#conditional-expressions)")
        content.append("- [Window Functions](#window-functions)")
        content.append("- [Subqueries & Exists](#subqueries--exists)")
        content.append("- [Model-Specific Examples](#model-specific-examples)")
        
        # Basic aggregation functions
        content.extend(self.generate_basic_aggregations())
        
        # Annotation functions
        content.extend(self.generate_annotation_functions())
        
        # String functions
        content.extend(self.generate_string_functions())
        
        # Date/Time functions
        content.extend(self.generate_datetime_functions())
        
        # Conditional expressions
        content.extend(self.generate_conditional_expressions())
        
        # Window functions
        content.extend(self.generate_window_functions())
        
        # Subqueries
        content.extend(self.generate_subquery_functions())
        
        # Model-specific examples
        content.append("\n---\n")
        content.append("## 🏗️ Model-Specific Examples")
        
        for model in models_to_analyze:
            content.extend(self.generate_model_aggregation_examples(model))
        
        return "\n".join(content)

    def generate_basic_aggregations(self):
        content = []
        content.append("\n---\n")
        content.append("## 📊 Basic Aggregation Functions")
        content.append("\nAggregation functions compute a single result from a set of values.")
        
        # Count
        content.append("\n### 🔢 Count")
        content.append("```python")
        content.append("# Basic count")
        content.append("Model.objects.count()")
        content.append("Model.objects.aggregate(total=Count('id'))")
        content.append("")
        content.append("# Count with conditions")
        content.append("Model.objects.filter(is_active=True).count()")
        content.append("Model.objects.aggregate(active_count=Count('id', filter=Q(is_active=True)))")
        content.append("")
        content.append("# Count distinct")
        content.append("Model.objects.aggregate(unique_categories=Count('category', distinct=True))")
        content.append("")
        content.append("# Count related objects")
        content.append("Model.objects.aggregate(related_count=Count('related_field'))")
        content.append("Model.objects.aggregate(related_distinct=Count('related_field', distinct=True))")
        content.append("```")
        
        # Sum
        content.append("\n### ➕ Sum")
        content.append("```python")
        content.append("# Basic sum")
        content.append("Model.objects.aggregate(total_amount=Sum('amount'))")
        content.append("")
        content.append("# Sum with conditions")
        content.append("Model.objects.aggregate(")
        content.append("    positive_sum=Sum('amount', filter=Q(amount__gt=0))")
        content.append(")")
        content.append("")
        content.append("# Sum through relationships")
        content.append("Model.objects.aggregate(related_sum=Sum('related_field__amount'))")
        content.append("")
        content.append("# Sum with F expressions")
        content.append("Model.objects.aggregate(calculated_sum=Sum(F('price') * F('quantity')))")
        content.append("```")
        
        # Average
        content.append("\n### 📈 Average")
        content.append("```python")
        content.append("# Basic average")
        content.append("Model.objects.aggregate(avg_price=Avg('price'))")
        content.append("")
        content.append("# Average with conditions")
        content.append("Model.objects.aggregate(")
        content.append("    avg_active_price=Avg('price', filter=Q(is_active=True))")
        content.append(")")
        content.append("")
        content.append("# Average through relationships")
        content.append("Model.objects.aggregate(avg_related=Avg('related_field__score'))")
        content.append("```")
        
        # Max/Min
        content.append("\n### ⬆️⬇️ Max & Min")
        content.append("```python")
        content.append("# Basic max/min")
        content.append("Model.objects.aggregate(")
        content.append("    max_price=Max('price'),")
        content.append("    min_price=Min('price')")
        content.append(")")
        content.append("")
        content.append("# Max/Min with conditions")
        content.append("Model.objects.aggregate(")
        content.append("    max_active_price=Max('price', filter=Q(is_active=True)),")
        content.append("    min_active_price=Min('price', filter=Q(is_active=True))")
        content.append(")")
        content.append("")
        content.append("# Max/Min dates")
        content.append("Model.objects.aggregate(")
        content.append("    latest_date=Max('created_at'),")
        content.append("    earliest_date=Min('created_at')")
        content.append(")")
        content.append("```")
        
        # Standard Deviation & Variance
        content.append("\n### 📏 Standard Deviation & Variance")
        content.append("```python")
        content.append("# Standard deviation")
        content.append("Model.objects.aggregate(")
        content.append("    price_stddev=StdDev('price'),")
        content.append("    price_variance=Variance('price')")
        content.append(")")
        content.append("")
        content.append("# Population vs Sample")
        content.append("from django.db.models import StdDev, Variance")
        content.append("Model.objects.aggregate(")
        content.append("    sample_stddev=StdDev('price', sample=True),")
        content.append("    population_stddev=StdDev('price', sample=False)")
        content.append(")")
        content.append("```")
        
        return content

    def generate_annotation_functions(self):
        content = []
        content.append("\n---\n")
        content.append("## 🏷️ Annotation Functions")
        content.append("\nAnnotations add calculated fields to each object in a QuerySet.")
        
        # Basic annotations
        content.append("\n### 🔢 Count Annotations")
        content.append("```python")
        content.append("# Annotate with related object counts")
        content.append("Model.objects.annotate(")
        content.append("    comment_count=Count('comments'),")
        content.append("    tag_count=Count('tags'),")
        content.append("    active_comment_count=Count('comments', filter=Q(comments__is_active=True))")
        content.append(")")
        content.append("")
        content.append("# Multiple count annotations")
        content.append("queryset = Model.objects.annotate(")
        content.append("    total_related=Count('related_field'),")
        content.append("    distinct_categories=Count('category', distinct=True),")
        content.append("    recent_items=Count('items', filter=Q(items__created_at__gte=timezone.now() - timedelta(days=30)))")
        content.append(")")
        content.append("```")
        
        # Numeric annotations
        content.append("\n### 📊 Numeric Annotations")
        content.append("```python")
        content.append("# Sum, Avg, Max, Min annotations")
        content.append("Model.objects.annotate(")
        content.append("    total_amount=Sum('transactions__amount'),")
        content.append("    avg_rating=Avg('reviews__rating'),")
        content.append("    max_score=Max('scores__value'),")
        content.append("    min_score=Min('scores__value')")
        content.append(")")
        content.append("")
        content.append("# Calculated fields with F expressions")
        content.append("Model.objects.annotate(")
        content.append("    total_value=F('price') * F('quantity'),")
        content.append("    discount_price=F('price') * (1 - F('discount_rate')),")
        content.append("    profit_margin=F('selling_price') - F('cost_price')")
        content.append(")")
        content.append("```")
        
        # Conditional annotations
        content.append("\n### 🔀 Conditional Annotations")
        content.append("```python")
        content.append("# Boolean annotations")
        content.append("Model.objects.annotate(")
        content.append("    is_expensive=Case(")
        content.append("        When(price__gt=1000, then=Value(True)),")
        content.append("        default=Value(False),")
        content.append("        output_field=BooleanField()")
        content.append("    ),")
        content.append("    has_discount=Case(")
        content.append("        When(discount_rate__gt=0, then=Value(True)),")
        content.append("        default=Value(False),")
        content.append("        output_field=BooleanField()")
        content.append("    )")
        content.append(")")
        content.append("")
        content.append("# Category annotations")
        content.append("Model.objects.annotate(")
        content.append("    price_category=Case(")
        content.append("        When(price__lt=100, then=Value('Cheap')),")
        content.append("        When(price__lt=500, then=Value('Moderate')),")
        content.append("        When(price__lt=1000, then=Value('Expensive')),")
        content.append("        default=Value('Premium'),")
        content.append("        output_field=CharField()")
        content.append("    )")
        content.append(")")
        content.append("```")
        
        return content

    def generate_string_functions(self):
        content = []
        content.append("\n---\n")
        content.append("## 🔤 String Functions")
        content.append("\nString manipulation functions for text fields.")
        
        content.append("\n### 🔡 Basic String Operations")
        content.append("```python")
        content.append("# Case conversion")
        content.append("Model.objects.annotate(")
        content.append("    name_upper=Upper('name'),")
        content.append("    name_lower=Lower('name'),")
        content.append("    title_length=Length('title')")
        content.append(")")
        content.append("")
        content.append("# String concatenation")
        content.append("Model.objects.annotate(")
        content.append("    full_name=Concat('first_name', Value(' '), 'last_name'),")
        content.append("    display_name=Concat('title', Value(' - '), 'category__name'),")
        content.append("    formatted_price=Concat(Value('$'), 'price')")
        content.append(")")
        content.append("")
        content.append("# Substring operations")
        content.append("Model.objects.annotate(")
        content.append("    short_description=Substr('description', 1, 100),")
        content.append("    first_char=Substr('name', 1, 1),")
        content.append("    last_three_chars=Substr('code', -3)")
        content.append(")")
        content.append("```")
        
        content.append("\n### 🔍 Advanced String Functions")
        content.append("```python")
        content.append("# String replacement and manipulation")
        content.append("from django.db.models.functions import Replace, Trim, LTrim, RTrim")
        content.append("")
        content.append("Model.objects.annotate(")
        content.append("    clean_name=Trim('name'),")
        content.append("    formatted_phone=Replace('phone', Value('-'), Value('')),")
        content.append("    display_code=Upper(Substr('code', 1, 3))")
        content.append(")")
        content.append("")
        content.append("# Conditional string operations")
        content.append("Model.objects.annotate(")
        content.append("    display_title=Case(")
        content.append("        When(title__isnull=True, then=Value('No Title')),")
        content.append("        default=Upper('title'),")
        content.append("        output_field=CharField()")
        content.append("    )")
        content.append(")")
        content.append("```")
        
        return content

    def generate_datetime_functions(self):
        content = []
        content.append("\n---\n")
        content.append("## 📅 Date/Time Functions")
        content.append("\nDate and time manipulation functions.")
        
        content.append("\n### 📆 Date Extraction")
        content.append("```python")
        content.append("# Extract date parts")
        content.append("Model.objects.annotate(")
        content.append("    created_year=Extract('created_at', 'year'),")
        content.append("    created_month=Extract('created_at', 'month'),")
        content.append("    created_day=Extract('created_at', 'day'),")
        content.append("    created_weekday=Extract('created_at', 'week_day'),")
        content.append("    created_hour=Extract('created_at', 'hour')")
        content.append(")")
        content.append("")
        content.append("# Date truncation")
        content.append("Model.objects.annotate(")
        content.append("    created_year_start=TruncYear('created_at'),")
        content.append("    created_month_start=TruncMonth('created_at'),")
        content.append("    created_day_start=TruncDay('created_at')")
        content.append(")")
        content.append("```")
        
        content.append("\n### ⏰ Time Calculations")
        content.append("```python")
        content.append("from django.utils import timezone")
        content.append("from datetime import timedelta")
        content.append("")
        content.append("# Age calculations")
        content.append("Model.objects.annotate(")
        content.append("    age_days=(timezone.now() - F('created_at')),")
        content.append("    is_recent=Case(")
        content.append("        When(created_at__gte=timezone.now() - timedelta(days=7), then=Value(True)),")
        content.append("        default=Value(False),")
        content.append("        output_field=BooleanField()")
        content.append("    )")
        content.append(")")
        content.append("")
        content.append("# Duration between dates")
        content.append("Model.objects.annotate(")
        content.append("    processing_time=F('completed_at') - F('started_at'),")
        content.append("    is_overdue=Case(")
        content.append("        When(due_date__lt=timezone.now(), then=Value(True)),")
        content.append("        default=Value(False),")
        content.append("        output_field=BooleanField()")
        content.append("    )")
        content.append(")")
        content.append("```")
        
        return content

    def generate_conditional_expressions(self):
        content = []
        content.append("\n---\n")
        content.append("## 🔀 Conditional Expressions")
        content.append("\nConditional logic in queries using Case/When statements.")
        
        content.append("\n### 🎯 Case/When Statements")
        content.append("```python")
        content.append("# Simple conditional")
        content.append("Model.objects.annotate(")
        content.append("    status_display=Case(")
        content.append("        When(status=1, then=Value('Active')),")
        content.append("        When(status=2, then=Value('Inactive')),")
        content.append("        When(status=3, then=Value('Pending')),")
        content.append("        default=Value('Unknown'),")
        content.append("        output_field=CharField()")
        content.append("    )")
        content.append(")")
        content.append("")
        content.append("# Multiple conditions")
        content.append("Model.objects.annotate(")
        content.append("    priority_level=Case(")
        content.append("        When(Q(is_urgent=True) & Q(importance__gte=8), then=Value('Critical')),")
        content.append("        When(Q(is_urgent=True) | Q(importance__gte=6), then=Value('High')),")
        content.append("        When(importance__gte=4, then=Value('Medium')),")
        content.append("        default=Value('Low'),")
        content.append("        output_field=CharField()")
        content.append("    )")
        content.append(")")
        content.append("```")
        
        content.append("\n### 🔧 Coalesce & Greatest/Least")
        content.append("```python")
        content.append("# Handle NULL values")
        content.append("Model.objects.annotate(")
        content.append("    display_name=Coalesce('nickname', 'first_name', Value('Anonymous')),")
        content.append("    safe_price=Coalesce('sale_price', 'regular_price', Value(0)),")
        content.append("    description_or_default=Coalesce('description', Value('No description available'))")
        content.append(")")
        content.append("")
        content.append("# Greatest and Least")
        content.append("Model.objects.annotate(")
        content.append("    max_price=Greatest('regular_price', 'sale_price'),")
        content.append("    min_price=Least('regular_price', 'sale_price'),")
        content.append("    best_score=Greatest('score1', 'score2', 'score3')")
        content.append(")")
        content.append("```")
        
        return content

    def generate_window_functions(self):
        content = []
        content.append("\n---\n")
        content.append("## 🪟 Window Functions")
        content.append("\nWindow functions perform calculations across related rows (Django 2.0+).")
        
        content.append("\n### 📊 Ranking Functions")
        content.append("```python")
        content.append("from django.db.models import Window")
        content.append("from django.db.models.functions import RowNumber, Rank, DenseRank")
        content.append("")
        content.append("# Row numbering")
        content.append("Model.objects.annotate(")
        content.append("    row_number=Window(")
        content.append("        expression=RowNumber(),")
        content.append("        order_by=F('created_at').desc()")
        content.append("    )")
        content.append(")")
        content.append("")
        content.append("# Ranking by score")
        content.append("Model.objects.annotate(")
        content.append("    rank=Window(")
        content.append("        expression=Rank(),")
        content.append("        order_by=F('score').desc()")
        content.append("    ),")
        content.append("    dense_rank=Window(")
        content.append("        expression=DenseRank(),")
        content.append("        order_by=F('score').desc()")
        content.append("    )")
        content.append(")")
        content.append("```")
        
        content.append("\n### 🔄 Lag/Lead Functions")
        content.append("```python")
        content.append("from django.db.models.functions import Lag, Lead")
        content.append("")
        content.append("# Previous and next values")
        content.append("Model.objects.annotate(")
        content.append("    previous_price=Window(")
        content.append("        expression=Lag('price', offset=1),")
        content.append("        order_by='created_at'")
        content.append("    ),")
        content.append("    next_price=Window(")
        content.append("        expression=Lead('price', offset=1),")
        content.append("        order_by='created_at'")
        content.append("    )")
        content.append(")")
        content.append("")
        content.append("# Price change calculation")
        content.append("Model.objects.annotate(")
        content.append("    previous_price=Window(")
        content.append("        expression=Lag('price'),")
        content.append("        order_by='created_at'")
        content.append("    )")
        content.append(").annotate(")
        content.append("    price_change=F('price') - F('previous_price')")
        content.append(")")
        content.append("```")
        
        content.append("\n### 📈 Partitioned Window Functions")
        content.append("```python")
        content.append("# Ranking within groups")
        content.append("Model.objects.annotate(")
        content.append("    category_rank=Window(")
        content.append("        expression=Rank(),")
        content.append("        partition_by=['category'],")
        content.append("        order_by=F('score').desc()")
        content.append("    ),")
        content.append("    category_row_number=Window(")
        content.append("        expression=RowNumber(),")
        content.append("        partition_by=['category'],")
        content.append("        order_by=F('created_at').desc()")
        content.append("    )")
        content.append(")")
        content.append("```")
        
        return content

    def generate_subquery_functions(self):
        content = []
        content.append("\n---\n")
        content.append("## 🔍 Subqueries & Exists")
        content.append("\nSubqueries and existence checks for complex filtering.")
        
        content.append("\n### 🎯 Exists Annotations")
        content.append("```python")
        content.append("# Check if related objects exist")
        content.append("Model.objects.annotate(")
        content.append("    has_comments=Exists(")
        content.append("        Comment.objects.filter(post=OuterRef('pk'))")
        content.append("    ),")
        content.append("    has_recent_activity=Exists(")
        content.append("        Activity.objects.filter(")
        content.append("            model_id=OuterRef('pk'),")
        content.append("            created_at__gte=timezone.now() - timedelta(days=30)")
        content.append("        )")
        content.append("    )")
        content.append(")")
        content.append("```")
        
        content.append("\n### 📊 Subquery Annotations")
        content.append("```python")
        content.append("# Get values from related models")
        content.append("latest_comment = Comment.objects.filter(")
        content.append("    post=OuterRef('pk')")
        content.append(").order_by('-created_at')")
        content.append("")
        content.append("Model.objects.annotate(")
        content.append("    latest_comment_text=Subquery(")
        content.append("        latest_comment.values('text')[:1]")
        content.append("    ),")
        content.append("    latest_comment_date=Subquery(")
        content.append("        latest_comment.values('created_at')[:1]")
        content.append("    )")
        content.append(")")
        content.append("")
        content.append("# Aggregate subqueries")
        content.append("Model.objects.annotate(")
        content.append("    avg_related_score=Subquery(")
        content.append("        RelatedModel.objects.filter(")
        content.append("            parent=OuterRef('pk')")
        content.append("        ).aggregate(avg_score=Avg('score'))['avg_score']")
        content.append("    )")
        content.append(")")
        content.append("```")
        
        content.append("\n### 🔗 Complex Subquery Examples")
        content.append("```python")
        content.append("# Conditional subqueries")
        content.append("high_priority_tasks = Task.objects.filter(")
        content.append("    project=OuterRef('pk'),")
        content.append("    priority__gte=8")
        content.append(")")
        content.append("")
        content.append("Project.objects.annotate(")
        content.append("    has_high_priority_tasks=Exists(high_priority_tasks),")
        content.append("    high_priority_count=Subquery(")
        content.append("        high_priority_tasks.aggregate(count=Count('id'))['count']")
        content.append("    )")
        content.append(")")
        content.append("")
        content.append("# Nested subqueries")
        content.append("Model.objects.annotate(")
        content.append("    top_related_item=Subquery(")
        content.append("        RelatedModel.objects.filter(")
        content.append("            parent=OuterRef('pk')")
        content.append("        ).order_by('-score').values('name')[:1]")
        content.append("    )")
        content.append(")")
        content.append("```")
        
        return content

    def generate_model_aggregation_examples(self, model):
        model_name = model.__name__
        app_name = model._meta.app_label
        content = []
        
        content.append(f"\n### 🏗️ {model_name} ({app_name})")
        content.append(f"\n**Database Table:** `{model._meta.db_table}`")
        
        # Analyze fields for specific examples
        numeric_fields = []
        string_fields = []
        date_fields = []
        fk_fields = []
        m2m_fields = []
        reverse_fk_fields = []
        reverse_m2m_fields = []
        
        for field in model._meta.get_fields():
            if isinstance(field, models.Field):
                if isinstance(field, (models.IntegerField, models.FloatField, models.DecimalField)):
                    numeric_fields.append(field.name)
                elif isinstance(field, (models.CharField, models.TextField)):
                    string_fields.append(field.name)
                elif isinstance(field, (models.DateField, models.DateTimeField)):
                    date_fields.append(field.name)
                elif isinstance(field, models.ForeignKey):
                    fk_fields.append((field.name, field.related_model.__name__))
                elif isinstance(field, models.ManyToManyField):
                    m2m_fields.append((field.name, field.related_model.__name__))
            elif isinstance(field, ManyToOneRel):
                reverse_fk_fields.append((field.name, field.related_model.__name__))
            elif isinstance(field, ManyToManyRel):
                reverse_m2m_fields.append((field.name, field.related_model.__name__))

        # Generate specific examples
        content.append(f"\n#### 📊 Aggregation Examples")
        content.append("```python")
        
        # Basic aggregations
        content.append(f"# Basic aggregations for {model_name}")
        content.append(f"stats = {model_name}.objects.aggregate(")
        content.append("    total_count=Count('id'),")
        
        if numeric_fields:
            field = numeric_fields[0]
            content.append(f"    {field}_sum=Sum('{field}'),")
            content.append(f"    {field}_avg=Avg('{field}'),")
            content.append(f"    {field}_max=Max('{field}'),")
            content.append(f"    {field}_min=Min('{field}'),")
        
        if date_fields:
            field = date_fields[0]
            content.append(f"    latest_{field}=Max('{field}'),")
            content.append(f"    earliest_{field}=Min('{field}'),")
        
        content.append(")")
        content.append("")
        
        # Annotations
        content.append(f"# Annotation examples for {model_name}")
        content.append(f"queryset = {model_name}.objects.annotate(")
        
        annotations = []
        
        # Count annotations
        for field_name, related_model in reverse_fk_fields[:2]:  # Limit to first 2
            annotations.append(f"    {field_name}_count=Count('{field_name}')")
        
        for field_name, related_model in m2m_fields[:2]:  # Limit to first 2
            annotations.append(f"    {field_name}_count=Count('{field_name}')")
        
        # Numeric annotations
        if numeric_fields:
            field = numeric_fields[0]
            annotations.append(f"    {field}_doubled=F('{field}') * 2")
            if len(numeric_fields) > 1:
                field2 = numeric_fields[1]
                annotations.append(f"    {field}_{field2}_sum=F('{field}') + F('{field2}')")
        
        # String annotations
        if string_fields:
            field = string_fields[0]
            annotations.append(f"    {field}_upper=Upper('{field}')")
            annotations.append(f"    {field}_length=Length('{field}')")
        
        # Date annotations
        if date_fields:
            field = date_fields[0]
            annotations.append(f"    {field}_year=Extract('{field}', 'year')")
            annotations.append(f"    {field}_month=Extract('{field}', 'month')")
        
        # Conditional annotations
        if numeric_fields:
            field = numeric_fields[0]
            annotations.append(f"    is_high_{field}=Case(")
            annotations.append(f"        When({field}__gt=100, then=Value(True)),")
            annotations.append(f"        default=Value(False),")
            annotations.append(f"        output_field=BooleanField()")
            annotations.append(f"    )")
        
        if annotations:
            content.extend(annotations[:10])  # Limit to first 10 annotations
        
        content.append(")")
        content.append("```")
        
        # Grouping examples
        if string_fields or fk_fields:
            content.append(f"\n#### 📈 Grouping Examples")
            content.append("```python")
            content.append(f"# Group by examples for {model_name}")
            
            if string_fields:
                field = string_fields[0]
                content.append(f"# Group by {field}")
                content.append(f"grouped = {model_name}.objects.values('{field}').annotate(")
                content.append("    count=Count('id'),")
                if numeric_fields:
                    num_field = numeric_fields[0]
                    content.append(f"    avg_{num_field}=Avg('{num_field}'),")
                    content.append(f"    sum_{num_field}=Sum('{num_field}'),")
                    content.append(f"    max_{num_field}=Max('{num_field}'),")
                    content.append(f"    min_{num_field}=Min('{num_field}')")
                content.append(").order_by('-count')")
                content.append("")
            
            if fk_fields:
                fk_field, related_model = fk_fields[0]
                content.append(f"# Group by {related_model}")
                content.append(f"grouped_by_fk = {model_name}.objects.values('{fk_field}__{string_fields[0] if string_fields else 'id'}').annotate(")
                content.append("    count=Count('id'),")
                if numeric_fields:
                    num_field = numeric_fields[0]
                    content.append(f"    total_{num_field}=Sum('{num_field}')")
                content.append(").order_by('-count')")
                content.append("")
            
            if date_fields:
                date_field = date_fields[0]
                content.append(f"# Group by date periods")
                content.append(f"by_year = {model_name}.objects.annotate(")
                content.append(f"    year=Extract('{date_field}', 'year')")
                content.append(").values('year').annotate(")
                content.append("    count=Count('id')")
                content.append(").order_by('year')")
                content.append("")
                
                content.append(f"by_month = {model_name}.objects.annotate(")
                content.append(f"    month=TruncMonth('{date_field}')")
                content.append(").values('month').annotate(")
                content.append("    count=Count('id')")
                content.append(").order_by('month')")
            
            content.append("```")
        
        # Complex query examples
        content.append(f"\n#### 🔥 Advanced Query Examples")
        content.append("```python")
        content.append(f"# Complex aggregations for {model_name}")
        
        # Multi-level aggregations
        if reverse_fk_fields and numeric_fields:
            rel_field, rel_model = reverse_fk_fields[0]
            num_field = numeric_fields[0]
            content.append(f"# Multi-level aggregation with conditions")
            content.append(f"complex_stats = {model_name}.objects.annotate(")
            content.append(f"    total_{rel_field}=Count('{rel_field}'),")
            content.append(f"    active_{rel_field}=Count('{rel_field}', filter=Q({rel_field}__is_active=True)),")
            content.append(f"    avg_{num_field}_per_{rel_field}=Avg('{rel_field}__{num_field}'),")
            content.append(f"    high_value_{rel_field}=Count('{rel_field}', filter=Q({rel_field}__{num_field}__gt=100))")
            content.append(")")
            content.append("")
        
        # Window function examples
        if numeric_fields:
            num_field = numeric_fields[0]
            content.append(f"# Window functions")
            content.append(f"ranked = {model_name}.objects.annotate(")
            content.append(f"    rank=Window(")
            content.append(f"        expression=Rank(),")
            content.append(f"        order_by=F('{num_field}').desc()")
            content.append(f"    ),")
            content.append(f"    row_num=Window(")
            content.append(f"        expression=RowNumber(),")
            content.append(f"        order_by=F('{num_field}').desc()")
            content.append(f"    )")
            content.append(")")
            content.append("")
        
        # Subquery examples
        if reverse_fk_fields:
            rel_field, rel_model = reverse_fk_fields[0]
            content.append(f"# Subquery examples")
            content.append(f"with_latest_{rel_field} = {model_name}.objects.annotate(")
            content.append(f"    latest_{rel_field}_id=Subquery(")
            content.append(f"        {rel_model}.objects.filter(")
            content.append(f"            {model_name.lower()}=OuterRef('pk')")
            content.append(f"        ).order_by('-id').values('id')[:1]")
            content.append(f"    ),")
            content.append(f"    has_{rel_field}=Exists(")
            content.append(f"        {rel_model}.objects.filter({model_name.lower()}=OuterRef('pk'))")
            content.append(f"    )")
            content.append(")")
            content.append("")
        
        # Performance optimized queries
        content.append(f"# Performance optimized aggregations")
        content.append(f"optimized = {model_name}.objects.select_related(")
        if fk_fields:
            fk_names = [f"'{fk[0]}'" for fk in fk_fields[:3]]
            content.append(f"    {', '.join(fk_names)}")
        content.append(").prefetch_related(")
        if m2m_fields:
            m2m_names = [f"'{m2m[0]}'" for m2m in m2m_fields[:3]]
            content.append(f"    {', '.join(m2m_names)}")
        content.append(").annotate(")
        
        final_annotations = []
        if reverse_fk_fields:
            for rel_field, _ in reverse_fk_fields[:2]:
                final_annotations.append(f"    {rel_field}_count=Count('{rel_field}')")
        if numeric_fields:
            field = numeric_fields[0]
            final_annotations.append(f"    {field}_category=Case(")
            final_annotations.append(f"        When({field}__lt=50, then=Value('Low')),")
            final_annotations.append(f"        When({field}__lt=100, then=Value('Medium')),")
            final_annotations.append(f"        default=Value('High'),")
            final_annotations.append(f"        output_field=CharField()")
            final_annotations.append(f"    )")
        
        if final_annotations:
            content.extend(final_annotations)
        content.append(")")
        
        content.append("```")
        content.append("")
        
        # Add simple for loop print examples
        content.append(f"\n#### 🖨️ Simple Print Examples")
        content.append("```python")
        content.append(f"# Simple for loop to print annotated {model_name} values")
        content.append(f"queryset = {model_name}.objects.annotate(")
        
        # Add the most common annotations for printing
        print_annotations = []
        
        # Count annotations
        for field_name, related_model in reverse_fk_fields[:2]:
            print_annotations.append(f"    {field_name}_count=Count('{field_name}'),")
        
        # Numeric calculations
        if numeric_fields:
            field = numeric_fields[0]
            print_annotations.append(f"    {field}_doubled=F('{field}') * 2,")
            if len(numeric_fields) > 1:
                field2 = numeric_fields[1]
                print_annotations.append(f"    {field}_{field2}_sum=F('{field}') + F('{field2}'),")
        
        # String functions
        if string_fields:
            field = string_fields[0]
            print_annotations.append(f"    {field}_upper=Upper('{field}'),")
            print_annotations.append(f"    {field}_length=Length('{field}'),")
        
        # Boolean conditions
        if numeric_fields:
            field = numeric_fields[0]
            print_annotations.append(f"    is_high_{field}=Case(")
            print_annotations.append(f"        When({field}__gt=100, then=Value(True)),")
            print_annotations.append(f"        default=Value(False),")
            print_annotations.append(f"        output_field=BooleanField()")
            print_annotations.append(f"    )")
        
        if print_annotations:
            content.extend(print_annotations)
        
        content.append(")")
        content.append("")
        content.append(f"# Simple one-line print")
        content.append(f"for item in queryset:")
        
        # Build print statement
        print_fields = []
        if hasattr(model, 'id'):
            print_fields.append("ID: {item.id}")
        
        if string_fields:
            field = string_fields[0]
            print_fields.append(f"{field.title()}: {{item.{field}}}")
        
        # Add annotated fields to print
        for field_name, _ in reverse_fk_fields[:2]:
            print_fields.append(f"{field_name.title()} Count: {{item.{field_name}_count}}")
        
        if numeric_fields:
            field = numeric_fields[0]
            print_fields.append(f"{field.title()} Doubled: {{item.{field}_doubled}}")
            if len(numeric_fields) > 1:
                field2 = numeric_fields[1]
                print_fields.append(f"{field.title()}+{field2.title()}: {{item.{field}_{field2}_sum}}")
        
        if string_fields:
            field = string_fields[0]
            print_fields.append(f"{field.title()} Upper: {{item.{field}_upper}}")
            print_fields.append(f"{field.title()} Length: {{item.{field}_length}}")
        
        if numeric_fields:
            field = numeric_fields[0]
            print_fields.append(f"High {field.title()}: {{item.is_high_{field}}}")
        
        if print_fields:
            print_statement = ", ".join(print_fields)
            content.append(f"    print(f\"{print_statement}\")")
        
        content.append("")
        content.append(f"# Multi-line print for better readability")
        content.append(f"for item in queryset:")
        
        for field_desc in print_fields[:6]:  # Limit to first 6 fields
            field_part = field_desc.split(": {")[0] + ": {" + field_desc.split(": {")[1]
            content.append(f"    print(f\"{field_part}\")")
        
        content.append("    print('-' * 30)")
        content.append("")
        content.append(f"# Print aggregate statistics")
        content.append(f"stats = {model_name}.objects.aggregate(")
        content.append("    total_count=Count('id'),")
        
        if numeric_fields:
            field = numeric_fields[0]
            content.append(f"    {field}_avg=Avg('{field}'),")
            content.append(f"    {field}_sum=Sum('{field}'),")
            content.append(f"    {field}_max=Max('{field}'),")
            content.append(f"    {field}_min=Min('{field}')")
        
        content.append(")")
        content.append("print('=== AGGREGATE STATISTICS ===')")
        content.append("for key, value in stats.items():")
        content.append("    print(f\"{key}: {value}\")")
        
        content.append("```")
        content.append("")
        
        return content