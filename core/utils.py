from django.db.models import Model, DateTimeField, SlugField
from django.utils.text import slugify

class BaseTimeStamp(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class SlugBaseModel(Model):
    slug = SlugField(
        unique=True,
        blank=True,
        null=True,
        max_length=200
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            # On cherche 'title', sinon 'name', sinon None
            value = getattr(self, 'title', getattr(self, 'name', None))
            if value:
                self.slug = slugify(value)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

