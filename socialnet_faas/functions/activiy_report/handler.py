import json
from datetime import datetime
from collections import defaultdict

def handler(event, context=None):
    try:
        data = json.loads(event['body']) if 'body' in event else event
        return analyze_user_performance(data)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def analyze_user_performance(data):
    user = data['user']
    posts = data['posts']
    current_time = datetime.fromisoformat(data['current_time'].replace('Z', '+00:00'))

    summary = calculate_summary(posts)
    engagement = calculate_engagement(posts, user['followers']['current'])
    followers_growth = calculate_followers_growth(user['followers'])
    top_posts = get_top_posts(posts)
    best_times = get_best_times(posts)
    quality_scores = calculate_quality_scores(posts, current_time)

    result = {
        'summary': summary,
        'engagement': engagement,
        'followers_growth': followers_growth,
        'top_posts': top_posts,
        'best_times': best_times,
        'quality_scores': quality_scores
    }

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }

def calculate_summary(posts):
    return {
        'post_count': len(posts),
        'like_count': sum(post['likes'] for post in posts),
        'comment_count': sum(post['comments'] for post in posts),
        'share_count': sum(post['shares'] for post in posts)
    }

def calculate_engagement(posts, current_followers):
    total_engagements = sum(post['likes'] + post['comments'] + post['shares'] for post in posts)
    total_impressions = sum(post['impressions'] for post in posts)

    followers_based = total_engagements / current_followers if current_followers > 0 else 0
    impressions_based = total_engagements / total_impressions if total_impressions > 0 else 0

    return {
        'followers_based': round(followers_based, 4),
        'impressions_based': round(impressions_based, 4)
    }

def calculate_followers_growth(followers):
    absolute_growth = followers['current'] - followers['previous']
    growth_rate = (absolute_growth / followers['previous'] * 100) if followers['previous'] > 0 else 0

    return {
        'absolute': absolute_growth,
        'percent': round(growth_rate, 2)
    }

def get_top_posts(posts):
    scored_posts = []
    for post in posts:
        score = post['likes'] + post['comments'] + post['shares']
        scored_posts.append({
            'id': post['id'],
            'score': score,
            'likes': post['likes'],
            'comments': post['comments'],
            'shares': post['shares'],
            'timestamp': post['timestamp']
        })

    return sorted(scored_posts, key=lambda x: x['score'], reverse=True)[:3]

def get_best_times(posts):
    hour_engagement = defaultdict(int)

    for post in posts:
        timestamp = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))
        hour = timestamp.hour
        engagement = post['likes'] + post['comments'] + post['shares']
        hour_engagement[hour] += engagement

    sorted_hours = sorted(hour_engagement.items(), key=lambda x: x[1], reverse=True)

    return [
        {'hour': hour, 'engagement': engagement}
        for hour, engagement in sorted_hours[:3]
    ]


def calculate_quality_scores(posts, current_time):
    loyalty = calculate_loyalty_score(posts)
    recency = calculate_recency_score(posts, current_time)
    frequency = calculate_frequency_score(posts)

    return {
        'loyalty': round(loyalty, 4),
        'recency': round(recency, 4),
        'frequency': round(frequency, 4)
    }

def calculate_loyalty_score(posts):
    all_engaged_users = set()
    for post in posts:
        all_engaged_users.update(post['engaged_users'])

    user_post_count = defaultdict(int)
    for post in posts:
        for user in post['engaged_users']:
            user_post_count[user] += 1

    returning_users = sum(1 for count in user_post_count.values() if count > 1)
    total_active_users = len(all_engaged_users)

    return returning_users / total_active_users if total_active_users > 0 else 0

def calculate_recency_score(posts, current_time):
    if not posts:
        return 0

    latest_timestamp = max(
        datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))
        for post in posts
    )

    days_since_last = (current_time - latest_timestamp).days
    return 1 / (1 + days_since_last)

def calculate_frequency_score(posts):
    total_engagements = sum(post['likes'] + post['comments'] + post['shares'] for post in posts)

    all_engaged_users = set()
    for post in posts:
        all_engaged_users.update(post['engaged_users'])

    unique_active_users = len(all_engaged_users)

    return total_engagements / unique_active_users if unique_active_users > 0 else 0
