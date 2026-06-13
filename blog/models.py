from django.db import models
from django.utils.text import slugify
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published')]

    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True, max_length=320)
    excerpt = models.TextField(max_length=500, help_text='Short summary for listings')
    body = models.TextField(help_text='Write in Markdown')
    cover_image = models.ImageField(upload_to='covers/', null=True, blank=True)
    category = models.ForeignKey(
        Category, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='posts'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reading_time = models.PositiveIntegerField(default=1, editable=False)
    views = models.PositiveIntegerField(default=0, editable=False)

    def _compute_reading_time(self):
        word_count = len(self.body.split())
        return max(1, round(word_count / 200))  # 200 wpm

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        self.reading_time = self._compute_reading_time()
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_at']
