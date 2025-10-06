from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.db import transaction

from posts.models import Post
from faas.interface import FaasService


FAAS_URL = settings.FAAS_URL

@receiver(post_save, sender=Post)
def call_faas_upon_post_creation(sender, instance, created, **kwargs):
    print("Post created signal received. Created:", created, "Post ID:", instance.id)
    # Call the FAAS functions only after the transaction is committed, to ensure the Post is saved
    transaction.on_commit(lambda: _call_faas_for_post(instance, created))


def _call_faas_for_post(instance: Post, created: bool):
    if created:
        faas = FaasService()
        callback = settings.FAAS_CALLBACK_URL
        
        faas.call_function(
            faas.function_categorize_post_text,
            payload={"text": instance.content, "unique_id": instance.id},
            is_async=True,
            callback_hook=callback,
        )
        faas.call_function(
            faas.function_extract_keywords,
            payload={"text": instance.content, "unique_id": instance.id},
            is_async=True,
            callback_hook=callback,
        )
        faas.call_function(
            faas.function_sentiment_analysis,
            payload=instance.content or "",
            is_async=True,
            metadata={"unique_id": instance.id},
            callback_hook=callback,
        )
        if instance.image:
            bucket = instance.image.storage.bucket_name
            key = instance.image.name
            output_key = f"thumbnails/{key}"
            w, h = 150, 150
            faas.call_function(
                faas.function_image_thumbnail,
                payload={"bucket": bucket, "key": key, "output_key": output_key, "size": [w, h], "unique_id": instance.id},
                is_async=True,
            callback_hook=callback,
            )
        if instance.video:
            bucket = instance.image.storage.bucket_name
            key = instance.video.name
            # output_key name is the same as video name, but with .jpeg
            output_key = f"thumbnails/{'.'.join(key.split('.')[:-1])}.jpeg"
            w, h = 150, 150
            faas.call_function(
                faas.function_video_thumbnail,
                payload={"bucket": bucket, "key": key, "output_key": output_key, "size": [w, h], "unique_id": instance.id},
                is_async=True,
                callback_hook=callback,
            )

        # TODO: MAKE SYNC TO STOP BAD POST FROM BEING SAVED
        faas.call_function(
            faas.function_offensive_word_detection,
            payload={"text": instance.content, "unique_id": instance.id},
            is_async=True,
            callback_hook=callback,
        )
