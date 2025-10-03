import json
from faas.interface import FaasService, get_metadata_from_cache


def process_callback_data(request):
    function_name = request.headers.get('X-Function-Name', 'Unknown')
    print(f"Processing callback from function: {function_name}")
    status = request.headers.get('X-Function-Status', 'Unknown')
    print(f"Function Status: {status}")
    call_id = request.headers.get('X-Call-Id', 'Unknown')
    print(f"Function Call ID: {call_id}")
    
    if status != '200':
        error = request.body.decode('utf-8') or 'No error message provided'
        print("Function execution failed or did not complete successfully:", error)
        return
    
    try:
        data = request.body.decode('utf-8')
        data = json.loads(data) if data else {}
        print("Callback Data:", data)
    except Exception as e:
        print("Error processing callback data:", str(e))
        return
    
    match function_name:
        case FaasService.function_generate_report:
            # No async call
            pass

        case FaasService.function_offensive_word_detection:
            # {"censored": "str", "found_words": ["str", "str", ...], "toxic": true, "unique_id": int}

            post_id = data.get("unique_id")
            censored = data.get("censored")
            found_words = data.get("found_words", [])
            toxic = data.get("toxic", False)
            print(f"Post ID: {post_id}, Censored: {censored}, Found Words: {found_words}, Toxic: {toxic}")

            if not post_id:
                print("No unique_id provided in callback data.")
                return

            from posts.models import Post
            try:
                post = Post.objects.get(id=post_id)
                post.is_toxit = toxic
                post.is_offensive = bool(found_words)
                post.is_blocked_by_system = post.is_offensive and post.is_toxit
                post.save(update_fields=['is_toxit', 'is_offensive', 'is_blocked_by_system', 'updated_at'])
                print(f"Post {post_id} offensiveness updated successfully.")
            except Post.DoesNotExist:
                print(f"Post with ID {post_id} does not exist.")
            except Exception as e:
                print(f"Error updating Post {post_id}: {str(e)}")

        case FaasService.function_extract_keywords:
            # {"keywords": ["str", "str", ...], "unique_id": int}
            
            post_id = data.get("unique_id")
            keywords = data.get("keywords", [])
            print(f"Post ID: {post_id}, Keywords: {keywords}")
            if not post_id:
                print("No unique_id provided in callback data.")
                return
            
            from posts.models import Post
            try:
                post = Post.objects.get(id=post_id)
                post.keywords = keywords
                post.save(update_fields=['keywords', 'updated_at'])
                print(f"Post {post_id} keywords updated successfully.")
            except Post.DoesNotExist:
                print(f"Post with ID {post_id} does not exist.")
            except Exception as e:
                print(f"Error updating Post {post_id}: {str(e)}")
        
        case FaasService.function_image_thumbnail | FaasService.function_video_thumbnail:
            # {"output_key": "str", "size": [w, h], "unique_id": int}
            
            post_id = data.get("unique_id")
            keywords = data.get("keywords", [])
            print(f"Post ID: {post_id}, Keywords: {keywords}")
            if not post_id:
                print("No unique_id provided in callback data.")
                return
            
            from posts.models import Post
            try:
                post = Post.objects.get(id=post_id)
                post.thumbnail.name = data.get("output_key", "")
                post.save(update_fields=['thumbnail', 'updated_at'])
                print(f"Post {post_id} thumbnail updated successfully.")
            except Post.DoesNotExist:
                print(f"Post with ID {post_id} does not exist.")
            except Exception as e:
                print(f"Error updating Post {post_id}: {str(e)}")

        case FaasService.function_categorize_post_text:
            # {"topics": [{"lable": "str", "score": float}, ...], "unique_id": int}
            
            post_id = data.get("unique_id")
            topics = data.get("topics", [])
            print(f"Post ID: {post_id}, Topics: {topics}")
            if not post_id:
                print("No unique_id provided in callback data.")
                return
            
            from posts.models import Post
            try:
                post = Post.objects.get(id=post_id)
                # For simplicity, just store the top topic as sentiment
                if topics:
                    top_topic = max(topics, key=lambda x: x.get("score", 0))
                    if top_topic.get("score", 0) > 0.3:  # threshold
                        post.topic = top_topic.get("label", "")
                        post.save(update_fields=['topic', 'updated_at'])
                print(f"Post {post_id} topic updated successfully.")
            except Post.DoesNotExist:
                print(f"Post with ID {post_id} does not exist.")
            except Exception as e:
                print(f"Error updating Post {post_id}: {str(e)}")
        
        case FaasService.function_sentiment_analysis:
            # { "polarity": float(-1 - 1),  "subjectivity": float (0 - 1), "sentence_count": 1 }
            
            post_id = get_metadata_from_cache(call_id)
            if post_id and isinstance(post_id, dict): post_id = post_id.get("unique_id", post_id)
            polarity = data.get("polarity", None)
            print(f"Post ID: {post_id}, Polarity: {polarity}")

            if not post_id:
                print("No post_id found in cache for call-id", call_id)
                return

            if polarity is None:
                print("Coudln't get the polarity from response", data)
                return
            
            # Polarity mapping
            if polarity > 0.05:
                sentiment = "positive"
            elif polarity < -0.05:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            from posts.models import Post
            try:
                post = Post.objects.get(id=post_id)
                post.sentiment = sentiment
                post.save(update_fields=['sentiment', 'updated_at'])
                print(f"Post {post_id} sentiment updated successfully to {sentiment}.")
            except Post.DoesNotExist:
                print(f"Post with ID {post_id} does not exist.")
            except Exception as e:
                print(f"Error updating Post {post_id}: {str(e)}")
        
        
        case FaasService.function_image_inception:
            # [ {"score": float, "name": "str"}, ...]

            post_id = get_metadata_from_cache(call_id)
            if post_id and isinstance(post_id, dict): post_id = post_id.get("unique_id", post_id)
            tags: list[dict] = data
            print(f"Post ID: {post_id}, tags: {tags}")

            if not post_id:
                print("No post_id found in cache for call-id", call_id)
                return

            if not tags:
                print("Coudln't find any tags in data", data)
                return

            tags = sorted(tags, key=lambda x: x.get("score", 0), reverse=True)[:5]
            tags = [tag.get("name", "") for tag in tags if tag.get("name", "")]
            print(f"Top tags: {tags}")
            
            from posts.models import Post
            try:
                post = Post.objects.get(id=post_id)
                post.tags = tags
                post.save(update_fields=['tags', 'updated_at'])
                print(f"Post {post_id} tags updated successfully to {tags}.")
            except Post.DoesNotExist:
                print(f"Post with ID {post_id} does not exist.")
            except Exception as e:
                print(f"Error updating Post {post_id}: {str(e)}")
            
        
        case FaasService.function_nsfw_recognition:
            # Not used yet
            pass
        
        case FaasService.function_text_to_speech:
            # No async call
            pass
        
        case FaasService.function_text_to_qrcode:
            # No async call
            pass
        
        case _:
            print("Invalid function name:", function_name)
            return
        
        