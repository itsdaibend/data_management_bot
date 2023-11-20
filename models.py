from tortoise import fields
from tortoise.models import Model


class User(Model):
    user_id = fields.BigIntField(pk=True)
    is_superuser = fields.BooleanField(default=False)

    class Meta:
        table = "users"

    def __str__(self):
        return f"{self.user_id}"


class Category(Model):
    id = fields.IntField(pk=True, generated=True)
    owner_id = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    name = fields.CharField(max_length=255)

    class Meta:
        table = "categories"

    def __str__(self):
        return f"{self.name}"


class SubCategory(Model):
    id = fields.IntField(pk=True, generated=True)
    name = fields.CharField(max_length=255)
    category = fields.ForeignKeyField("models.Category", related_name="subcategories")
    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.CharField(max_length=255)

    class Meta:
        table = "subcategories"

    def __str__(self):
        return f"[{self.category}] {self.name}"


class SubCategoryData(Model):
    id = fields.IntField(pk=True, generated=True)
    subcategory = fields.ForeignKeyField(
        "models.SubCategory", related_name="data_entries"
    )
    file_id = fields.CharField(max_length=4096)
    file_type = fields.CharField(max_length=50)
    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.CharField(max_length=255)

    class Meta:
        table = "data_entries"

    def __str__(self):
        return f"[{self.subcategory} - {self.file_type}] {self.id}"


class CategoryData(Model):
    id = fields.IntField(pk=True, generated=True)
    category = fields.ForeignKeyField(
        "models.Category", related_name="category_data_entries"
    )
    file_id = fields.CharField(max_length=4096)
    file_type = fields.CharField(max_length=50)
    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.CharField(max_length=255)

    class Meta:
        table = "category_data_entries"

    def __str__(self):
        return f"[{self.category} - {self.file_type}] {self.id}"


class ChildCategory(Model):
    id = fields.IntField(pk=True, generated=True)
    name = fields.CharField(max_length=255)
    subcategory = fields.ForeignKeyField(
        "models.SubCategory", related_name="chlidcategories"
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.CharField(max_length=255)

    class Meta:
        table = "childcategories"

    def __str__(self):
        return f"[{self.subcategory}] {self.name}"


class ChildCategoryData(Model):
    id = fields.IntField(pk=True, generated=True)
    childcategory = fields.ForeignKeyField(
        "models.ChildCategory", related_name="child_data_entries"
    )
    file_id = fields.CharField(max_length=4096)
    file_type = fields.CharField(max_length=50)
    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.CharField(max_length=255)

    class Meta:
        table = "child_data_entries"

    def __str__(self):
        return f"[{self.childcategory} - {self.file_type}] {self.id}"
