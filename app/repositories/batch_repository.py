from app.extensions import db
from app.models.batch import Batch, BatchHospitalResult


class BatchRepository:
    def create_batch(self, batch: Batch) -> Batch:
        db.session.add(batch)
        db.session.commit()
        return batch

    def update_batch(self, batch: Batch) -> Batch:
        db.session.commit()
        return batch

    def get_by_id(self, batch_id: str) -> Batch | None:
        return Batch.query.get(batch_id)  # type: ignore

    def add_result(self, result: BatchHospitalResult) -> BatchHospitalResult:
        db.session.add(result)
        db.session.commit()
        return result

    def add_results(self, results: list[BatchHospitalResult]) -> None:
        db.session.add_all(results)
        db.session.commit()
