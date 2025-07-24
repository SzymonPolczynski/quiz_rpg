from django.urls import path
from . import views

urlpatterns = [
    path("", views.base_view, name="base"),
    path("home/", views.home_view, name="home"),
    path("quiz/", views.quiz_view, name="quiz"),
    path("choose_class/", views.choose_class_view, name="choose_class"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/allocate/", views.allocate_stats_view, name="allocate_stats"),
    path("inventory/", views.inventory_view, name="inventory"),
    path("use_item/<int:item_id>/", views.use_item_view, name="use_item"),
    path("equip_item/<int:item_id>/", views.equip_item_view, name="equip_item"),
    path("unequip_item/<str:slot>/", views.unequip_item_view, name="unequip_item"),
    path("quiz/choose_category/", views.choose_category_view, name="choose_category"),
    path(
        "quiz/set_category/<int:category_id>/",
        views.set_category_view,
        name="set_category",
    ),
    path("quiz/clear_category/", views.clear_category_view, name="clear_category"),
    path("shop/", views.shop_view, name="shop"),
    path("shop/buy/<int:item_id>/", views.buy_item_view, name="buy_item"),
    path("shop/sell/<int:item_id>/", views.sell_item_view, name="sell_item"),
    path("quests/", views.quest_list_view, name="quest_list"),
    path("quests/accept/<int:quest_id>/", views.accept_quest_view, name="accept_quest"),
    path("quest_log/", views.quest_log_view, name="quest_log"),
    path("quest_log/claim/<int:progress_id>/", views.claim_quest_reward_view, name="claim_quest_reward"),
]
