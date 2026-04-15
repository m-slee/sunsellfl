from django.urls import path

from . import views

app_name = "marketplace"

urlpatterns = [
    path("", views.HomePageView.as_view(), name="index"),
    path("about/", views.AboutPageView.as_view(), name="about"),
    path("legal/", views.LegalPageView.as_view(), name="legal"),
    path("contact/", views.ContactPageView.as_view(), name="contact"),
    path("contact_success/", views.ContactSuccessView.as_view(), name="contact_success"),
    path("listings/", views.ListingsPageView.as_view(), name="listings"),
    path("listings/create/", views.CreateListingView.as_view(), name="create_listing"),
    # path("payement_success/", views.ListingPaymentSuccess.as_view(), name="stripe_success"),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('stripe/success/', views.stripe_success, name='stripe_success'),
    path("listings/edit/<int:pk>/", views.EditListingView.as_view(), name="edit_listing"),
    path("listings/delete/<int:pk>/", views.DeleteListingView.as_view(), name="delete_listing"),
    path("listings/<str:category>/", views.ListingsPageView.as_view(), name="listings"),
    path("listing/<int:pk>/", views.ListingDetailView.as_view(), name="listing_detail"),
    path("listing/<int:listing_id>/reply/", views.ReplyCreateView.as_view(), name="reply_create"),
    path("account/", views.AccountListingsView.as_view(), name="account_listings"),
    path("account/info/", views.AccountInfoView.as_view(), name="account_info"),
    path("account/messages/", views.AccountMessagesView.as_view(), name="account_messages"),
    path("account/<int:listing_id>/replies/", views.RepliesListView.as_view(), name="replies_list"),
    path("account/<int:listing_id>/convo/<int:sender_id>/", views.ConversationDetailView.as_view(), name="conversation_detail"),
    path("account/<int:listing_id>/convo/<int:sender_id>/reply/", views.ConversationReplyCreate.as_view(), name="conversation_reply"),
]