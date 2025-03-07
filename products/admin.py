from django.contrib import admin
from .models import (
    Category, 
    Product, 
    InventoryTransaction, 
    Supplier, 
    Purchase, 
    PurchaseItem,
    AuditLog
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    fields = ('product', 'quantity', 'unit_price', 'total_price')
    readonly_fields = ('total_price',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('item_code', 'name', 'category', 'buying_price', 'selling_price', 
                   'current_stock', 'status', 'created_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('item_code', 'name', 'description')
    readonly_fields = ('created_by', 'updated_by', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('item_code', 'name', 'description', 'category')
        }),
        ('Pricing', {
            'fields': ('buying_price', 'selling_price')
        }),
        ('Inventory', {
            'fields': ('current_stock', 'reorder_level', 'status')
        }),
        ('Audit', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'transaction_type', 'quantity', 'unit_price', 
                   'total_amount', 'created_by', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('product__name', 'product__item_code', 'reference_number')
    readonly_fields = ('created_by', 'created_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone', 'created_at')
    search_fields = ('name', 'contact_person', 'email', 'phone')
    list_filter = ('created_at',)
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'supplier', 'purchase_date', 'status', 
                   'total_amount', 'created_by', 'created_at')
    list_filter = ('status', 'purchase_date', 'created_at')
    search_fields = ('reference_number', 'supplier__name')
    readonly_fields = ('created_by', 'updated_by', 'created_at', 'updated_at')
    inlines = [PurchaseItemInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'model_name', 'object_repr', 'user', 'timestamp')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('object_repr', 'user__username')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'object_repr', 'changes', 'timestamp')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
