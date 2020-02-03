from __future__ import absolute_import

import six
from uuid import uuid4

from django.core.urlresolvers import reverse

from sentry.utils.compat.mock import patch
from sentry.testutils import APITestCase


class ProjectRuleTaskDetailsTest(APITestCase):
    def setUp(self):
        self.login_as(user=self.user)
        team = self.create_team()
        project1 = self.create_project(teams=[team], name="foo", fire_project_created=True)
        self.create_project(teams=[team], name="bar", fire_project_created=True)
        self.rule = project1.rule_set.all()[0]
        self.uuid = uuid4().hex
        self.url = reverse(
            "sentry-api-0-project-rule-task-details",
            kwargs={
                "organization_slug": project1.organization.slug,
                "project_slug": project1.slug,
                "task_uuid": self.uuid,
            },
        )

    @patch("sentry.api.endpoints.project_rule_task_details._get_value_from_redis")
    def test_status_pending(self, mock_get_from_redis):
        self.login_as(user=self.user)
        mock_get_from_redis.return_value = {"status": "pending", "rule_id": None}
        response = self.client.get(self.url, format="json")

        assert response.status_code == 200, response.content
        assert response.data["status"] == "pending"
        assert response.data["rule"] is None

    @patch("sentry.api.endpoints.project_rule_task_details._get_value_from_redis")
    def test_status_failed(self, mock_get_from_redis):
        self.login_as(user=self.user)
        mock_get_from_redis.return_value = {"status": "failed", "rule_id": None}
        response = self.client.get(self.url, format="json")

        assert response.status_code == 200, response.content
        assert response.data["status"] == "failed"
        assert response.data["rule"] is None

    @patch("sentry.api.endpoints.project_rule_task_details._get_value_from_redis")
    def test_status_success(self, mock_get_from_redis):
        self.login_as(user=self.user)
        mock_get_from_redis.return_value = {"status": "success", "rule_id": self.rule.id}
        response = self.client.get(self.url, format="json")

        assert response.status_code == 200, response.content
        assert response.data["status"] == "success"

        rule_data = response.data["rule"]
        # TODO(meredith): shoudl I check every attribute?
        assert rule_data["id"] == six.text_type(self.rule.id)
        assert rule_data["name"] == self.rule.label
