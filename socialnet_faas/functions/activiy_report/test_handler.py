import json
import unittest
from datetime import datetime
from handler import (
    handler, analyze_user_performance, calculate_summary,
    calculate_engagement, calculate_followers_growth, get_top_posts,
    get_best_times, calculate_quality_scores,
    calculate_loyalty_score, calculate_recency_score, calculate_frequency_score
)

class TestActivityReportHandler(unittest.TestCase):

    def setUp(self):
        self.sample_data = {
            "user": {
                "id": "u123",
                "followers": {
                    "current": 6050,
                    "previous": 5900
                }
            },
            "posts": [
                {
                    "id": "p1",
                    "timestamp": "2025-09-01T14:00:00Z",
                    "likes": 120,
                    "comments": 15,
                    "shares": 8,
                    "impressions": 1500,
                    "engaged_users": ["u1", "u2", "u3"]
                },
                {
                    "id": "p2",
                    "timestamp": "2025-09-02T18:00:00Z",
                    "likes": 90,
                    "comments": 12,
                    "shares": 5,
                    "impressions": 1100,
                    "engaged_users": ["u2", "u4"]
                },
                {
                    "id": "p3",
                    "timestamp": "2025-09-03T10:00:00Z",
                    "likes": 200,
                    "comments": 25,
                    "shares": 15,
                    "impressions": 2000,
                    "engaged_users": ["u1", "u3", "u5"]
                }
            ],
            "current_time": "2025-09-23T20:00:00Z"
        }

    def test_lambda_handler_success(self):
        """Test successful lambda handler execution"""
        event = {"body": json.dumps(self.sample_data)}
        response = handler(event)

        self.assertEqual(response['statusCode'], 200)
        result = json.loads(response['body'])

        # Verify all required sections are present
        required_sections = ['summary', 'engagement', 'followers_growth',
                           'top_posts', 'best_times', 'quality_scores']
        for section in required_sections:
            self.assertIn(section, result)

    def test_lambda_handler_direct_event(self):
        """Test handler with direct event (no body wrapper)"""
        response = handler(self.sample_data)

        self.assertEqual(response['statusCode'], 200)
        result = json.loads(response['body'])
        self.assertIn('summary', result)

    def test_lambda_handler_error(self):
        """Test error handling in lambda handler"""
        invalid_event = {"body": "invalid json"}
        response = handler(invalid_event)

        self.assertEqual(response['statusCode'], 500)
        error_body = json.loads(response['body'])
        self.assertIn('error', error_body)

    def test_calculate_summary(self):
        """Test activity summary calculation"""
        result = calculate_summary(self.sample_data['posts'])

        expected = {
            'post_count': 3,
            'like_count': 410,  # 120 + 90 + 200
            'comment_count': 52,  # 15 + 12 + 25
            'share_count': 28  # 8 + 5 + 15
        }

        self.assertEqual(result, expected)

    def test_calculate_summary_empty_posts(self):
        """Test summary calculation with no posts"""
        result = calculate_summary([])

        expected = {
            'post_count': 0,
            'like_count': 0,
            'comment_count': 0,
            'share_count': 0
        }

        self.assertEqual(result, expected)

    def test_calculate_engagement(self):
        """Test engagement rate calculation"""
        posts = self.sample_data['posts']
        result = calculate_engagement(posts, 6050)

        total_engagements = 490  # 143 + 107 + 240
        total_impressions = 4600  # 1500 + 1100 + 2000

        expected_followers = round(total_engagements / 6050, 4)
        expected_impressions = round(total_engagements / total_impressions, 4)

        self.assertEqual(result['followers_based'], expected_followers)
        self.assertEqual(result['impressions_based'], expected_impressions)

    def test_calculate_engagement_zero_followers(self):
        """Test engagement calculation with zero followers"""
        result = calculate_engagement(self.sample_data['posts'], 0)

        self.assertEqual(result['followers_based'], 0)
        self.assertGreater(result['impressions_based'], 0)

    def test_calculate_engagement_zero_impressions(self):
        """Test engagement calculation with zero impressions"""
        posts_no_impressions = [
            {"likes": 10, "comments": 5, "shares": 2, "impressions": 0}
        ]
        result = calculate_engagement(posts_no_impressions, 1000)

        self.assertEqual(result['impressions_based'], 0)
        self.assertGreater(result['followers_based'], 0)

    def test_calculate_followers_growth(self):
        """Test followers growth calculation"""
        followers = {"current": 6050, "previous": 5900}
        result = calculate_followers_growth(followers)

        expected_absolute = 150
        expected_percent = round((150 / 5900) * 100, 2)

        self.assertEqual(result['absolute'], expected_absolute)
        self.assertEqual(result['percent'], expected_percent)

    def test_calculate_followers_growth_zero_previous(self):
        """Test followers growth with zero previous followers"""
        followers = {"current": 1000, "previous": 0}
        result = calculate_followers_growth(followers)

        self.assertEqual(result['absolute'], 1000)
        self.assertEqual(result['percent'], 0)

    def test_calculate_followers_growth_negative(self):
        """Test followers growth with negative growth"""
        followers = {"current": 5800, "previous": 6000}
        result = calculate_followers_growth(followers)

        self.assertEqual(result['absolute'], -200)
        self.assertEqual(result['percent'], round((-200 / 6000) * 100, 2))

    def test_get_top_posts(self):
        """Test top performing posts calculation"""
        result = get_top_posts(self.sample_data['posts'])

        # Should return posts sorted by engagement score (likes + comments + shares)
        # p3: 240, p1: 143, p2: 107
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['id'], 'p3')
        self.assertEqual(result[0]['score'], 240)
        self.assertEqual(result[1]['id'], 'p1')
        self.assertEqual(result[1]['score'], 143)
        self.assertEqual(result[2]['id'], 'p2')
        self.assertEqual(result[2]['score'], 107)

    def test_get_top_posts_fewer_than_three(self):
        """Test top posts with fewer than 3 posts"""
        single_post = [self.sample_data['posts'][0]]
        result = get_top_posts(single_post)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 'p1')

    def test_get_best_times(self):
        """Test best posting times calculation"""
        result = get_best_times(self.sample_data['posts'])

        # Posts are at hours 14, 18, 10 with engagements 143, 107, 240
        # Should be sorted: hour 10 (240), hour 14 (143), hour 18 (107)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['hour'], 10)
        self.assertEqual(result[0]['engagement'], 240)
        self.assertEqual(result[1]['hour'], 14)
        self.assertEqual(result[1]['engagement'], 143)

    def test_calculate_loyalty_score(self):
        """Test loyalty score calculation"""
        result = calculate_loyalty_score(self.sample_data['posts'])

        # Engaged users: u1, u2, u3 (p1), u2, u4 (p2), u1, u3, u5 (p3)
        # All users: u1, u2, u3, u4, u5 (5 total)
        # Returning users: u1 (p1,p3), u2 (p1,p2), u3 (p1,p3) = 3 users
        # Loyalty = 3/5 = 0.6
        expected = 3 / 5
        self.assertEqual(result, expected)

    def test_calculate_loyalty_score_no_posts(self):
        """Test loyalty score with no posts"""
        result = calculate_loyalty_score([])
        self.assertEqual(result, 0)

    def test_calculate_recency_score(self):
        """Test recency score calculation"""
        current_time = datetime.fromisoformat("2025-09-23T20:00:00+00:00")
        result = calculate_recency_score(self.sample_data['posts'], current_time)

        # Latest post is 2025-09-03, current time is 2025-09-23
        # Days difference = 20 days
        # Recency score = 1 / (1 + 20) = 1/21
        expected = 1 / (1 + 20)
        self.assertAlmostEqual(result, expected, places=6)

    def test_calculate_recency_score_no_posts(self):
        """Test recency score with no posts"""
        current_time = datetime.fromisoformat("2025-09-23T20:00:00+00:00")
        result = calculate_recency_score([], current_time)
        self.assertEqual(result, 0)

    def test_calculate_frequency_score(self):
        """Test frequency score calculation"""
        result = calculate_frequency_score(self.sample_data['posts'])

        # Total engagements: 490
        # Unique users: u1, u2, u3, u4, u5 = 5
        # Frequency = 490 / 5 = 98
        expected = 490 / 5
        self.assertEqual(result, expected)

    def test_calculate_frequency_score_no_users(self):
        """Test frequency score with no engaged users"""
        posts_no_users = [
            {"likes": 10, "comments": 5, "shares": 2, "engaged_users": []}
        ]
        result = calculate_frequency_score(posts_no_users)
        self.assertEqual(result, 0)

    def test_calculate_quality_scores(self):
        """Test quality scores calculation"""
        posts = self.sample_data['posts']
        current_time = datetime.fromisoformat("2025-09-23T20:00:00+00:00")

        result = calculate_quality_scores(posts, current_time)

        # Verify all scores are present and rounded to 4 decimal places
        self.assertIn('loyalty', result)
        self.assertIn('recency', result)
        self.assertIn('frequency', result)

        # Verify values are reasonable
        self.assertGreaterEqual(result['loyalty'], 0)
        self.assertLessEqual(result['loyalty'], 1)
        self.assertGreater(result['recency'], 0)
        self.assertGreater(result['frequency'], 0)

    def test_full_integration(self):
        """Test complete integration flow"""
        result = analyze_user_performance(self.sample_data)
        body = json.loads(result['body'])

        # Verify structure
        self.assertEqual(result['statusCode'], 200)

        # Verify summary
        self.assertEqual(body['summary']['post_count'], 3)
        self.assertEqual(body['summary']['like_count'], 410)

        # Verify engagement rates are reasonable
        self.assertGreater(body['engagement']['followers_based'], 0)
        self.assertGreater(body['engagement']['impressions_based'], 0)

        # Verify followers growth
        self.assertEqual(body['followers_growth']['absolute'], 150)

        # Verify top posts
        self.assertEqual(len(body['top_posts']), 3)
        self.assertEqual(body['top_posts'][0]['id'], 'p3')

        # Verify best times
        self.assertGreater(len(body['best_times']), 0)

        # Verify quality scores
        self.assertGreater(body['quality_scores']['loyalty'], 0)
        self.assertGreater(body['quality_scores']['recency'], 0)
        self.assertGreater(body['quality_scores']['frequency'], 0)

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
