import io


def test_bulk_upload_success(client, mocker):
    mocker.patch(
        "app.core.hospital_client.HospitalDirectoryClient.create_hospital",
        return_value={"id": 1},
    )
    mocker.patch(
        "app.core.hospital_client.HospitalDirectoryClient.activate_batch",
        return_value=None,
    )

    data = {"file": (io.BytesIO(b"name,address,phone\nH1,A1,\n"), "test.csv")}

    response = client.post(
        "/hospitals/bulk", data=data, content_type="multipart/form-data"
    )

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["total_hospitals"] == 1
    assert json_data["processed_hospitals"] == 1
    assert json_data["batch_activated"] is True
    assert len(json_data["hospitals"]) == 1


def test_bulk_upload_invalid_csv(client):
    data = {"file": (io.BytesIO(b"name,phone\nH1,P1\n"), "test.csv")}

    response = client.post(
        "/hospitals/bulk", data=data, content_type="multipart/form-data"
    )

    assert response.status_code == 400
    assert "Missing required columns" in response.get_json()["message"]


def test_bulk_upload_no_file(client):
    response = client.post("/hospitals/bulk")
    assert response.status_code == 422
