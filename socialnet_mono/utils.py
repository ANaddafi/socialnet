from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from posts.models import Post, Like, Repost
from follows.models import Follow

User = get_user_model()


def gather_user_analytics_data(user_id, days_back=30, previous_days_back=60):
    """
    Gather user analytics data for 3rd party API score calculation.

    Args:
        user_id: The ID of the user to analyze
        days_back: Number of days to look back for current data (default: 30)
        previous_days_back: Number of days to look back for previous period comparison (default: 60)

    Returns:
        dict: Formatted data matching the required schema
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

    current_time = timezone.now()
    current_period_start = current_time - timedelta(days=days_back)
    previous_period_start = current_time - timedelta(days=previous_days_back)
    previous_period_end = current_time - timedelta(days=days_back)

    # Get follower counts
    current_followers = Follow.objects.filter(target=user).count()
    previous_followers = Follow.objects.filter(
        target=user,
        created_at__lt=previous_period_end
    ).count()

    # Get user's posts from the current period
    posts = Post.objects.filter(
        author=user,
        created_at__gte=current_period_start,
        parent__isnull=True  # Exclude comments, only main posts
    ).order_by('-created_at')

    posts_data = []
    total_engagement = 0
    total_impressions = 0

    for post in posts:
        # Get likes for this post
        post_likes = Like.objects.filter(post=post)
        likes_count = post_likes.count()

        # Get comments (replies to this post)
        comments_count = Post.objects.filter(parent=post).count()

        # Get reposts/shares
        shares_count = Repost.objects.filter(post=post).count()

        # Calculate impressions (simplified - you may want to adjust this logic)
        # For now, using a formula based on followers + engagement
        impressions = max(
            current_followers + (likes_count + comments_count + shares_count) * 10,
            likes_count + comments_count + shares_count  # Minimum impressions
        )

        # Get engaged users (users who liked, commented, or shared)
        engaged_user_ids = set()

        # Add users who liked
        engaged_user_ids.update(
            post_likes.values_list('user_id', flat=True)
        )

        # Add users who commented
        engaged_user_ids.update(
            Post.objects.filter(parent=post).values_list('author_id', flat=True)
        )

        # Add users who shared/reposted
        engaged_user_ids.update(
            Repost.objects.filter(post=post).values_list('user_id', flat=True)
        )

        # Convert to list of user IDs as strings
        engaged_users = [f"u{uid}" for uid in engaged_user_ids]

        posts_data.append({
            "id": post.id,
            "timestamp": post.created_at.isoformat(),
            "likes": likes_count,
            "comments": comments_count,
            "shares": shares_count,
            "impressions": impressions,
            "engaged_users": engaged_users
        })

        # Accumulate totals for metrics calculation
        total_engagement += likes_count + comments_count + shares_count
        total_impressions += impressions

    return {
        "user": {
            "id": f"u{user.id}",
            "followers": {
                "current": current_followers,
                "previous": previous_followers
            }
        },
        "posts": posts_data,
        "current_time": current_time.isoformat()
    }


def gather_user_analytics_data_simple(user_id):
    """
    Simplified version with default parameters for quick usage.
    """
    return gather_user_analytics_data(user_id)
