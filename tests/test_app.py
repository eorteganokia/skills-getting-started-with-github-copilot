import copy
from fastapi.testclient import TestClient
import src.app as app_module

client = TestClient(app_module.app)

# Fixture pattern (manual) to isolate mutations on global activities
def reset_state():
    app_module.activities = copy.deepcopy(ORIGINAL)

ORIGINAL = copy.deepcopy(app_module.activities)


def test_get_activities_structure():
    reset_state()
    resp = client.get('/activities')
    assert resp.status_code == 200
    data = resp.json()
    # Ensure a couple expected keys exist
    assert 'Chess Club' in data
    chess = data['Chess Club']
    for key in ['description', 'schedule', 'max_participants', 'participants']:
        assert key in chess
    assert isinstance(chess['participants'], list)


def test_signup_new_participant():
    reset_state()
    email = 'new.student@mergington.edu'
    activity = 'Chess Club'
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in app_module.activities[activity]['participants']


def test_signup_duplicate_participant_returns_400():
    reset_state()
    existing = app_module.activities['Programming Class']['participants'][0]
    activity = 'Programming Class'
    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 400
    body = resp.json()
    assert 'already signed up' in body['detail']


def test_remove_participant_success():
    reset_state()
    activity = 'Gym Class'
    existing = app_module.activities[activity]['participants'][0]
    resp = client.delete(f"/activities/{activity}/participants?email={existing}")
    assert resp.status_code == 200
    assert existing not in app_module.activities[activity]['participants']


def test_remove_participant_not_found():
    reset_state()
    activity = 'Gym Class'
    email = 'not.enrolled@mergington.edu'
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404
    assert 'Participant not found' in resp.json()['detail']
