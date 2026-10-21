def make_exercise(client, name="Plank"):
    return client.post("/exercises", json={"name": name, "category": "Core"})


def make_workout(client):
    return client.post("/workouts", json={"date": "2026-10-19", "duration_minutes": 40, "notes": "Test"})


def test_create_and_list_exercises(client):
    assert make_exercise(client).status_code == 201
    res = client.get("/exercises")
    assert res.status_code == 200 and len(res.get_json()) == 1


def test_create_exercise_invalid(client):
    assert client.post("/exercises", json={"category": "Core"}).status_code == 400
    assert client.post("/exercises", json={"name": "   ", "category": "Core"}).status_code == 400


def test_duplicate_exercise_conflict(client):
    make_exercise(client)
    assert make_exercise(client).status_code == 409


def test_create_workout_invalid(client):
    res = client.post("/workouts", json={"date": "2026-10-19", "duration_minutes": -5})
    assert res.status_code == 400


def test_add_exercise_to_workout_and_show(client):
    wid = make_workout(client).get_json()["id"]
    eid = make_exercise(client).get_json()["id"]
    url = f"/workouts/{wid}/exercises/{eid}/workout_exercises"
    assert client.post(url, json={"sets": 3, "reps": 10}).status_code == 201
    assert client.post(url, json={"sets": 3, "reps": 10}).status_code == 409  # duplicate pair
    detail = client.get(f"/workouts/{wid}").get_json()
    assert detail["workout_exercises"][0]["reps"] == 10
    assert detail["workout_exercises"][0]["exercise"]["name"] == "Plank"
    assert client.get(f"/exercises/{eid}").get_json()["workout_exercises"][0]["workout"]["id"] == wid


def test_workout_exercise_requires_reps_or_duration(client):
    wid = make_workout(client).get_json()["id"]
    eid = make_exercise(client).get_json()["id"]
    res = client.post(f"/workouts/{wid}/exercises/{eid}/workout_exercises", json={"sets": 3})
    assert res.status_code == 400


def test_delete_workout_cascades(client):
    wid = make_workout(client).get_json()["id"]
    eid = make_exercise(client).get_json()["id"]
    client.post(f"/workouts/{wid}/exercises/{eid}/workout_exercises", json={"reps": 5})
    assert client.delete(f"/workouts/{wid}").status_code == 204
    assert client.get(f"/workouts/{wid}").status_code == 404
    assert client.get(f"/exercises/{eid}").get_json()["workout_exercises"] == []


def test_delete_exercise_and_404(client):
    eid = make_exercise(client).get_json()["id"]
    assert client.delete(f"/exercises/{eid}").status_code == 204
    assert client.delete(f"/exercises/{eid}").status_code == 404
