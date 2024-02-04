from django.contrib import admin
# from .models import related models
from .models import CarMake, CarModel


# Register your models here.


# CarModelInline class
class CarModelInline(admin.StackedInline):
    model = CarModel

# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]

# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]

# Register models here
    admin.site.register(CarMake, CarModelAdmin)
