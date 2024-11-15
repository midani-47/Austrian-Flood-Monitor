from django.db import models


class WaterLevel(models.Model):
    location_id = models.IntegerField(default=1)  # Example default
    value_at_time = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='cm')  # Already set
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "water_levels"  # Match the PostgreSQL table name


class Account(models.Model):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255, default='default_password')  # Default value
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts"  # Match the PostgreSQL table name