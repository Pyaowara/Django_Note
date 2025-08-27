# Django Model Query Guide

## Table of Contents

- [Company](#company)
- [Author](#author)
- [Publisher](#publisher)
- [Book](#book)
- [Store](#store)

---

## 📋 Company
> **Module**: `companies.models.Company`

**🗃️ Database Table**: `companies_company`


---

### 🚀 Basic Model Queries

```python
Company.objects.all()
Company.objects.count()
Company.objects.first()
Company.objects.last()
Company.objects.exists()
```

### 🔧 Field: `id`
**Type**: `BigAutoField`

```python
Company.objects.get(pk=1)
Company.objects.filter(pk__in=[1, 2, 3])
```

### 🔧 Field: `name`
**Type**: `CharField`

#### 📝 String Field Operations

```python
Company.objects.filter(name='exact_value')
Company.objects.filter(name__icontains='partial')
Company.objects.filter(name__startswith='prefix')
Company.objects.filter(name__endswith='suffix')
Company.objects.filter(name__isnull=False)
Company.objects.filter(name__regex=r'^[A-Z]')
```

### 🔧 Field: `ticker`
**Type**: `CharField`

#### 📝 String Field Operations

```python
Company.objects.filter(ticker='exact_value')
Company.objects.filter(ticker__icontains='partial')
Company.objects.filter(ticker__startswith='prefix')
Company.objects.filter(ticker__endswith='suffix')
Company.objects.filter(ticker__isnull=False)
Company.objects.filter(ticker__regex=r'^[A-Z]')
```

### 🔧 Field: `num_employees`
**Type**: `IntegerField`

#### 🔢 Numeric Field Operations

```python
Company.objects.filter(num_employees=100)
Company.objects.filter(num_employees__gt=100)
Company.objects.filter(num_employees__gte=100)
Company.objects.filter(num_employees__lt=200)
Company.objects.filter(num_employees__lte=200)
Company.objects.filter(num_employees__range=(50, 150))
Company.objects.filter(num_employees__in=[10, 20, 30])
```

### 🔧 Field: `num_tables`
**Type**: `IntegerField`

#### 🔢 Numeric Field Operations

```python
Company.objects.filter(num_tables=100)
Company.objects.filter(num_tables__gt=100)
Company.objects.filter(num_tables__gte=100)
Company.objects.filter(num_tables__lt=200)
Company.objects.filter(num_tables__lte=200)
Company.objects.filter(num_tables__range=(50, 150))
Company.objects.filter(num_tables__in=[10, 20, 30])
```

### 🔧 Field: `num_chairs`
**Type**: `IntegerField`

#### 🔢 Numeric Field Operations

```python
Company.objects.filter(num_chairs=100)
Company.objects.filter(num_chairs__gt=100)
Company.objects.filter(num_chairs__gte=100)
Company.objects.filter(num_chairs__lt=200)
Company.objects.filter(num_chairs__lte=200)
Company.objects.filter(num_chairs__range=(50, 150))
Company.objects.filter(num_chairs__in=[10, 20, 30])
```

### 📊 Aggregation Examples

**Import Required**: `from django.db.models import Count, Sum, Avg, Max, Min`

```python
Company.objects.aggregate(total=Count('id'))
Company.objects.aggregate(avg_id=Avg('id'))
Company.objects.aggregate(sum_id=Sum('id'))
```

#### Annotation examples

#### Advanced queries

```python
Company.objects.distinct()
Company.objects.order_by('id')
Company.objects.order_by('-id')  # Descending
Company.objects.values('field1', 'field2')
Company.objects.values_list('field1', flat=True)
```


---

## 📋 Author
> **Module**: `books.models.Author`

**🗃️ Database Table**: `books_author`


---

### 🚀 Basic Model Queries

```python
Author.objects.all()
Author.objects.count()
Author.objects.first()
Author.objects.last()
Author.objects.exists()
```

### 🔗 Reverse Relation: Many-to-Many (Reverse) from Book

#### Access from Author instance

```python
instance = Author.objects.get(pk=1)
instance.book.all()
instance.book.count()
instance.book.filter(some_field='value')
```

#### Query from Book side

```python
Book.objects.filter(authors__id=1)
Book.objects.filter(authors__name__icontains='value')
Book.objects.filter(authors__age__gt=100)
```

### 🔧 Field: `id`
**Type**: `BigAutoField`

```python
Author.objects.get(pk=1)
Author.objects.filter(pk__in=[1, 2, 3])
```

### 🔧 Field: `name`
**Type**: `CharField`

#### 📝 String Field Operations

```python
Author.objects.filter(name='exact_value')
Author.objects.filter(name__icontains='partial')
Author.objects.filter(name__startswith='prefix')
Author.objects.filter(name__endswith='suffix')
Author.objects.filter(name__isnull=False)
Author.objects.filter(name__regex=r'^[A-Z]')
```

### 🔧 Field: `age`
**Type**: `IntegerField`

#### 🔢 Numeric Field Operations

```python
Author.objects.filter(age=100)
Author.objects.filter(age__gt=100)
Author.objects.filter(age__gte=100)
Author.objects.filter(age__lt=200)
Author.objects.filter(age__lte=200)
Author.objects.filter(age__range=(50, 150))
Author.objects.filter(age__in=[10, 20, 30])
```

### 📊 Aggregation Examples

**Import Required**: `from django.db.models import Count, Sum, Avg, Max, Min`

```python
Author.objects.aggregate(total=Count('id'))
Author.objects.aggregate(avg_id=Avg('id'))
Author.objects.aggregate(sum_id=Sum('id'))
```

#### Annotation examples

#### Advanced queries

```python
Author.objects.distinct()
Author.objects.order_by('id')
Author.objects.order_by('-id')  # Descending
Author.objects.values('field1', 'field2')
Author.objects.values_list('field1', flat=True)
```


---

## 📋 Publisher
> **Module**: `books.models.Publisher`

**🗃️ Database Table**: `books_publisher`


---

### 🚀 Basic Model Queries

```python
Publisher.objects.all()
Publisher.objects.count()
Publisher.objects.first()
Publisher.objects.last()
Publisher.objects.exists()
```

### 🔗 Reverse Relation: One-to-Many (Reverse ForeignKey) from Book

#### Access from Publisher instance

```python
instance = Publisher.objects.get(pk=1)
instance.book.all()
instance.book.count()
instance.book.filter(some_field='value')
```

#### Query from Book side

```python
Book.objects.filter(publisher__id=1)
Book.objects.filter(publisher__name__icontains='value')
```

### 🔧 Field: `id`
**Type**: `BigAutoField`

```python
Publisher.objects.get(pk=1)
Publisher.objects.filter(pk__in=[1, 2, 3])
```

### 🔧 Field: `name`
**Type**: `CharField`

#### 📝 String Field Operations

```python
Publisher.objects.filter(name='exact_value')
Publisher.objects.filter(name__icontains='partial')
Publisher.objects.filter(name__startswith='prefix')
Publisher.objects.filter(name__endswith='suffix')
Publisher.objects.filter(name__isnull=False)
Publisher.objects.filter(name__regex=r'^[A-Z]')
```

### 📊 Aggregation Examples

**Import Required**: `from django.db.models import Count, Sum, Avg, Max, Min`

```python
Publisher.objects.aggregate(total=Count('id'))
Publisher.objects.aggregate(avg_id=Avg('id'))
Publisher.objects.aggregate(sum_id=Sum('id'))
```

#### Annotation examples

#### Advanced queries

```python
Publisher.objects.distinct()
Publisher.objects.order_by('id')
Publisher.objects.order_by('-id')  # Descending
Publisher.objects.values('field1', 'field2')
Publisher.objects.values_list('field1', flat=True)
```


---

## 📋 Book
> **Module**: `books.models.Book`

**🗃️ Database Table**: `books_book`


---

### 🚀 Basic Model Queries

```python
Book.objects.all()
Book.objects.count()
Book.objects.first()
Book.objects.last()
Book.objects.exists()
```

### 🔗 Reverse Relation: Many-to-Many (Reverse) from Store

#### Access from Book instance

```python
instance = Book.objects.get(pk=1)
instance.store.all()
instance.store.count()
instance.store.filter(some_field='value')
```

#### Query from Store side

```python
Store.objects.filter(books__id=1)
Store.objects.filter(books__name__icontains='value')
Store.objects.filter(books__pages__gt=100)
```

### 🔧 Field: `id`
**Type**: `BigAutoField`

```python
Book.objects.get(pk=1)
Book.objects.filter(pk__in=[1, 2, 3])
```

### 🔧 Field: `name`
**Type**: `CharField`

#### 📝 String Field Operations

```python
Book.objects.filter(name='exact_value')
Book.objects.filter(name__icontains='partial')
Book.objects.filter(name__startswith='prefix')
Book.objects.filter(name__endswith='suffix')
Book.objects.filter(name__isnull=False)
Book.objects.filter(name__regex=r'^[A-Z]')
```

### 🔧 Field: `pages`
**Type**: `IntegerField`

#### 🔢 Numeric Field Operations

```python
Book.objects.filter(pages=100)
Book.objects.filter(pages__gt=100)
Book.objects.filter(pages__gte=100)
Book.objects.filter(pages__lt=200)
Book.objects.filter(pages__lte=200)
Book.objects.filter(pages__range=(50, 150))
Book.objects.filter(pages__in=[10, 20, 30])
```

### 🔧 Field: `price`
**Type**: `DecimalField`

#### 🔢 Numeric Field Operations

```python
Book.objects.filter(price=100)
Book.objects.filter(price__gt=100)
Book.objects.filter(price__gte=100)
Book.objects.filter(price__lt=200)
Book.objects.filter(price__lte=200)
Book.objects.filter(price__range=(50, 150))
Book.objects.filter(price__in=[10, 20, 30])
```

### 🔧 Field: `rating`
**Type**: `FloatField`

#### 🔢 Numeric Field Operations

```python
Book.objects.filter(rating=100)
Book.objects.filter(rating__gt=100)
Book.objects.filter(rating__gte=100)
Book.objects.filter(rating__lt=200)
Book.objects.filter(rating__lte=200)
Book.objects.filter(rating__range=(50, 150))
Book.objects.filter(rating__in=[10, 20, 30])
```

### 🔧 Field: `publisher`
**Type**: `ForeignKey`

#### 🔗 ForeignKey to Publisher

#### 🔗 Basic ForeignKey queries

```python
Book.objects.filter(publisher_id=1)
Book.objects.filter(publisher__isnull=False)
Book.objects.filter(publisher__isnull=True)
Book.objects.select_related('publisher')
```

#### Filter through Publisher fields:

#### String field in Publisher

```python
Book.objects.filter(publisher__name='exact_value')
Book.objects.filter(publisher__name__icontains='partial')
Book.objects.filter(publisher__name__startswith='prefix')
Book.objects.filter(publisher__name__endswith='suffix')
Book.objects.filter(publisher__name__isnull=False)
```

#### 🔗 Complex ForeignKey queries

#### Multiple conditions on related model

**Import Required**: `from django.db.models import Q`

```python
Book.objects.filter(
Q(publisher__field1='value1') & Q(publisher__field2='value2')
)
```

#### Exclude queries

```python
Book.objects.exclude(publisher__isnull=True)
Book.objects.exclude(publisher__some_field='unwanted_value')
```

#### 🔗 Aggregation through ForeignKey

**Import Required**: `from django.db.models import Count`

```python
Book.objects.values('publisher__some_field').annotate(count=Count('id'))
```

#### 🔗 Ordering through ForeignKey

```python
Book.objects.order_by('publisher__some_field')
Book.objects.order_by('-publisher__some_field')
```

### 🔧 Field: `pubdate`
**Type**: `DateField`

#### 📅 Date/DateTime Field Operations

**Import Required**: `from django.utils import timezone`

**Import Required**: `from datetime import date, datetime`

```python
Book.objects.filter(pubdate__year=2025)
Book.objects.filter(pubdate__month=1)
Book.objects.filter(pubdate__day=15)
Book.objects.filter(pubdate__lt=timezone.now())
Book.objects.filter(pubdate__date=date.today())
```

### 🔧 Field: `authors`
**Type**: `ManyToManyField`

#### 🔄 ManyToMany field to Author

#### 🔄 Basic ManyToMany queries

```python
Book.objects.filter(authors__isnull=False)
Book.objects.filter(authors__id=1)
Book.objects.prefetch_related('authors')
```

#### Filter through Author fields:

```python
Book.objects.filter(authors__name__icontains='value')
Book.objects.filter(authors__age__gt=100)
```

#### 🔄 Instance-level ManyToMany operations

```python
instance = Book.objects.get(pk=1)
instance.authors.all()
instance.authors.count()
instance.authors.filter(some_field='value')
instance.authors.add(author_instance)
instance.authors.remove(author_instance)
instance.authors.clear()
```

### 📊 Aggregation Examples

**Import Required**: `from django.db.models import Count, Sum, Avg, Max, Min`

```python
Book.objects.aggregate(total=Count('id'))
Book.objects.aggregate(avg_id=Avg('id'))
Book.objects.aggregate(sum_id=Sum('id'))
```

#### Annotation examples

```python
Book.objects.annotate(related_count=Count('publisher'))
Book.objects.values('publisher__some_field').annotate(count=Count('id'))
```

#### Advanced queries

```python
Book.objects.distinct()
Book.objects.order_by('id')
Book.objects.order_by('-id')  # Descending
Book.objects.values('field1', 'field2')
Book.objects.values_list('field1', flat=True)
```

#### 🔗 Advanced ForeignKey queries

```python
Book.objects.select_related('publisher').order_by('publisher__some_field')
Book.objects.prefetch_related('publisher')
```


---

## 📋 Store
> **Module**: `books.models.Store`

**🗃️ Database Table**: `books_store`


---

### 🚀 Basic Model Queries

```python
Store.objects.all()
Store.objects.count()
Store.objects.first()
Store.objects.last()
Store.objects.exists()
```

### 🔧 Field: `id`
**Type**: `BigAutoField`

```python
Store.objects.get(pk=1)
Store.objects.filter(pk__in=[1, 2, 3])
```

### 🔧 Field: `name`
**Type**: `CharField`

#### 📝 String Field Operations

```python
Store.objects.filter(name='exact_value')
Store.objects.filter(name__icontains='partial')
Store.objects.filter(name__startswith='prefix')
Store.objects.filter(name__endswith='suffix')
Store.objects.filter(name__isnull=False)
Store.objects.filter(name__regex=r'^[A-Z]')
```

### 🔧 Field: `books`
**Type**: `ManyToManyField`

#### 🔄 ManyToMany field to Book

#### 🔄 Basic ManyToMany queries

```python
Store.objects.filter(books__isnull=False)
Store.objects.filter(books__id=1)
Store.objects.prefetch_related('books')
```

#### Filter through Book fields:

```python
Store.objects.filter(books__name__icontains='value')
Store.objects.filter(books__pages__gt=100)
Store.objects.filter(books__price__gt=100)
Store.objects.filter(books__rating__gt=100)
```

#### 🔄 Instance-level ManyToMany operations

```python
instance = Store.objects.get(pk=1)
instance.books.all()
instance.books.count()
instance.books.filter(some_field='value')
instance.books.add(book_instance)
instance.books.remove(book_instance)
instance.books.clear()
```

### 📊 Aggregation Examples

**Import Required**: `from django.db.models import Count, Sum, Avg, Max, Min`

```python
Store.objects.aggregate(total=Count('id'))
Store.objects.aggregate(avg_id=Avg('id'))
Store.objects.aggregate(sum_id=Sum('id'))
```

#### Annotation examples

#### Advanced queries

```python
Store.objects.distinct()
Store.objects.order_by('id')
Store.objects.order_by('-id')  # Descending
Store.objects.values('field1', 'field2')
Store.objects.values_list('field1', flat=True)
```

---

## 📚 Additional Resources

- [Django QuerySet API Reference](https://docs.djangoproject.com/en/stable/ref/models/querysets/)
- [Django Model Field Reference](https://docs.djangoproject.com/en/stable/ref/models/fields/)
- [Django Database Queries](https://docs.djangoproject.com/en/stable/topics/db/queries/)

*Generated on week5 Django project*