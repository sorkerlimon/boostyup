# Game Product Admin Start #
from django.contrib import admin
from .models import Game, GameProduct, GameProductDiamond, GameProductDiscount, GameProductTransaction


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'platform', 'language', 'region', 'is_active', 'is_featured', 'created_at')
    list_filter = ('platform', 'is_active', 'is_featured')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(GameProductDiamond)
class GameProductDiamondAdmin(admin.ModelAdmin):
    list_display = ('name', 'diamond_quantity', 'original_price', 'currency', 'is_active', 'is_featured', 'stock_quantity')
    list_filter = ('is_active', 'is_featured', 'currency')
    search_fields = ('name', 'diamond_quantity')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(GameProduct)
class GameProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'currency', 'is_active', 'is_featured', 'created_at')
    list_filter = ('game', 'is_active', 'is_featured', 'currency')
    search_fields = ('name', 'game__name', 'description')
    filter_horizontal = ('available_diamonds',)
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(GameProductDiscount)
class GameProductDiscountAdmin(admin.ModelAdmin):
    list_display = ('game_product_diamond', 'discount_percentage', 'discounted_price', 'created_at')
    list_filter = ('discount_percentage', 'created_at')
    search_fields = ('game_product_diamond__name',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'discounted_price')


@admin.register(GameProductTransaction)
class GameProductTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'game_product', 'game_product_diamond', 'final_price', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'user__email', 'game_product__name', 'game_product_diamond__name', 'in_game_player_id')
    readonly_fields = ('id', 'transaction_id', 'created_at', 'updated_at', 'completed_at', 'discount_amount', 'final_price')
    date_hierarchy = 'created_at'
# Game Product Admin End #
