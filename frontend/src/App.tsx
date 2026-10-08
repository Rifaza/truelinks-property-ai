
import { useEffect, useState } from "react";

import {
  uploadLease,
  acceptWorkOrder,
  analyzePhoto,
  createPropertyIssue,
  evaluateLease,
  getUnitOverview,
  rejectWorkOrder,
} from "./services/api";

import type { LeaseUploadResponse } from "./services/api";

import type {
  LeaseEvaluation,
  PropertyIssue,
  UnitOverview,
} from "./types/api";

import "./App.css";

const units = [
  { id: 1, label: "MC-B-1204 — Apartment 1204" },
  { id: 2, label: "MC-B-1205 — Apartment 1205" },
  { id: 3, label: "MC-B-0902 — Apartment 0902" },
  { id: 4, label: "MC-A-0301 — Apartment 0301" },
  { id: 5, label: "MC-A-0302 — Apartment 0302" },
];

function App() {
  const [selectedUnitId, setSelectedUnitId] = useState(1);
  const [unit, setUnit] = useState<UnitOverview | null>(null);
  const [evaluation, setEvaluation] =
    useState<LeaseEvaluation | null>(null);

  const [photo, setPhoto] = useState<File | null>(null);
  const [photoResult, setPhotoResult] =
    useState<PropertyIssue | null>(null);

  const [loading, setLoading] = useState(false);
  const [photoLoading, setPhotoLoading] = useState(false);
  const [error, setError] = useState("");

  const [leaseFile, setLeaseFile] = useState<File | null>(null);
  const [leaseUploadResult, setLeaseUploadResult] =
    useState<LeaseUploadResponse | null>(null);
  const [leaseUploading, setLeaseUploading] = useState(false);

  async function loadUnit() {
    try {
      setLoading(true);
      setError("");

      const result = await getUnitOverview(selectedUnitId);

      setUnit(result);
      setEvaluation(null);
      setPhotoResult(null);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load unit.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadUnit();
  }, [selectedUnitId]);

  async function handleEvaluateLease() {
    if (!unit?.lease) {
      return;
    }

    try {
      setError("");

      const result = await evaluateLease(unit.lease.id);

      setEvaluation(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to evaluate lease.",
      );
    }
  }

  async function handleAnalyzePhoto() {
    if (!photo || !unit) {
      return;
    }

    try {
      setPhotoLoading(true);
      setError("");

      const result = await analyzePhoto(
        photo,
        unit.unit_number,
      );

      setPhotoResult(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to analyze photo.",
      );
    } finally {
      setPhotoLoading(false);
    }
  }

  async function handleAcceptIssue() {
    if (!photoResult) {
      return;
    }

    try {
      setError("");

      await createPropertyIssue(
        selectedUnitId,
        photoResult,
      );

      setPhotoResult(null);
      setPhoto(null);

      await loadUnit();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to create property issue.",
      );
    }
  }

  async function handleWorkOrderDecision(
    workOrderId: number,
    accepted: boolean,
  ) {
    try {
      setError("");

      if (accepted) {
        await acceptWorkOrder(workOrderId);
      } else {
        await rejectWorkOrder(workOrderId);
      }

      await loadUnit();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to update work order.",
      );
    }
  }

  async function handleUploadLease() {
    if (!leaseFile) {
      return;
    }

    try {
      setLeaseUploading(true);
      setError("");
      setLeaseUploadResult(null);

      const result = await uploadLease(leaseFile);

      setLeaseUploadResult(result);

      // Refresh the selected unit to show persisted changes.
      await loadUnit();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to upload lease.",
      );
    } finally {
      setLeaseUploading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <p className="eyebrow">PROPERTY INTELLIGENCE</p>
          <h1>TrueLinks Property AI</h1>
          <p className="subtitle">
            Lease intelligence and maintenance issues in one view.
          </p>
        </div>
      </header>

      <main className="container">
        <section className="selector-card">
          <label htmlFor="unit">Property Unit</label>

          <select
            id="unit"
            value={selectedUnitId}
            onChange={(event) =>
              setSelectedUnitId(Number(event.target.value))
            }
          >
            {units.map((item) => (
              <option key={item.id} value={item.id}>
                {item.label}
              </option>
            ))}
          </select>
        </section>

        {/* Lease PDF upload and rule evaluation */}
        <section className="card">
          <div className="card-header">
            <div>
              <p className="eyebrow">LEASE INGESTION</p>
              <h3>Upload Lease Agreement</h3>
            </div>
          </div>

          <p className="muted">
            Upload a PDF to extract lease details and evaluate owner
            rules. Review the results before accepting the lease.
          </p>

          <input
            type="file"
            accept="application/pdf,.pdf"
            onChange={(event) =>
              setLeaseFile(event.target.files?.[0] ?? null)
            }
          />

          <button
            className="primary-button"
            disabled={!leaseFile || leaseUploading}
            onClick={handleUploadLease}
          >
            {leaseUploading
              ? "Processing..."
              : "Upload and Validate Lease"}
          </button>

          {leaseUploadResult && (
            <div className="review-panel">
              <p className="eyebrow">EXTRACTION RESULT</p>
              <h3>{leaseUploadResult.filename}</h3>

              <p>Lease ID: {leaseUploadResult.lease_id}</p>
              <p>Extracted unit: {leaseUploadResult.unit_number}</p>
              <p>Mode: {leaseUploadResult.extraction_mode}</p>
              <p>
                Human review required:{" "}
                {leaseUploadResult.human_review_required
                  ? "Yes"
                  : "No"}
              </p>

              <div className="rules">
                {leaseUploadResult.rules.map((rule) => (
                  <div className="rule" key={rule.rule_id}>
                    <div className="rule-top">
                      <strong>{rule.rule_id}</strong>
                      <span
                        className={`rule-status ${rule.status.toLowerCase()}`}
                      >
                        {rule.status}
                      </span>
                    </div>

                    <p>{rule.explanation}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        {error && <div className="error">{error}</div>}

        {loading && (
          <div className="loading">Loading unit...</div>
        )}

        {unit && !loading && (
          <>
            <section className="unit-header">
              <div>
                <p className="eyebrow">UNIT</p>
                <h2>{unit.unit_number}</h2>
                <p>{unit.label}</p>
              </div>

              <span className={`status ${unit.status.toLowerCase()}`}>
                {unit.status}
              </span>
            </section>

            <div className="grid">
              <section className="card">
                <div className="card-header">
                  <div>
                    <p className="eyebrow">LEASE</p>
                    <h3>Lease Record</h3>
                  </div>
                </div>

                {unit.lease ? (
                  <div className="details">
                    <div>
                      <span>Tenant</span>
                      <strong>
                        {unit.lease.tenant_name || "Not available"}
                      </strong>
                    </div>

                    <div>
                      <span>Monthly Rent</span>
                      <strong>
                        QAR {unit.lease.monthly_rent ?? "—"}
                      </strong>
                    </div>

                    <div>
                      <span>Annual Rent</span>
                      <strong>
                        QAR {unit.lease.annual_rent ?? "—"}
                      </strong>
                    </div>

                    <div>
                      <span>Deposit</span>
                      <strong>
                        QAR {unit.lease.deposit_amount ?? "—"}
                      </strong>
                    </div>

                    <div>
                      <span>Start</span>
                      <strong>{unit.lease.start_date ?? "—"}</strong>
                    </div>

                    <div>
                      <span>End</span>
                      <strong>{unit.lease.end_date ?? "—"}</strong>
                    </div>

                    <div>
                      <span>Term</span>
                      <strong>
                        {unit.lease.term_months ?? "—"} months
                      </strong>
                    </div>
                  </div>
                ) : (
                  <p className="muted">
                    No lease linked to this unit.
                  </p>
                )}

                {unit.lease && (
                  <button
                    className="secondary-button"
                    onClick={handleEvaluateLease}
                  >
                    Validate Lease
                  </button>
                )}
              </section>

              <section className="card">
                <div className="card-header">
                  <div>
                    <p className="eyebrow">PROPERTY</p>
                    <h3>Unit Information</h3>
                  </div>
                </div>

                <div className="details">
                  <div>
                    <span>Type</span>
                    <strong>{unit.unit_type}</strong>
                  </div>

                  <div>
                    <span>Area</span>
                    <strong>{unit.area_sqm} sqm</strong>
                  </div>

                  <div>
                    <span>Parking</span>
                    <strong>{unit.parking_bay || "—"}</strong>
                  </div>
                </div>
              </section>
            </div>

            {evaluation && (
              <section className="card">
                <div className="card-header">
                  <div>
                    <p className="eyebrow">OWNER RULES</p>
                    <h3>Lease Validation</h3>
                  </div>
                </div>

                <div className="rules">
                  {evaluation.rules.map((rule) => (
                    <div className="rule" key={rule.rule_id}>
                      <div className="rule-top">
                        <strong>{rule.rule_id}</strong>

                        <span
                          className={`rule-status ${rule.status.toLowerCase()}`}
                        >
                          {rule.status}
                        </span>
                      </div>

                      <p>{rule.explanation}</p>

                      {rule.evidence.length > 0 && (
                        <small>
                          Evidence:{" "}
                          {rule.evidence
                            .map((item) => item.field_name)
                            .join(", ")}
                        </small>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            )}

            <section className="card">
              <div className="card-header">
                <div>
                  <p className="eyebrow">MAINTENANCE</p>
                  <h3>Property Issues</h3>
                </div>
              </div>

              {unit.issues.length === 0 ? (
                <p className="muted">
                  No reported issues for this unit.
                </p>
              ) : (
                <div className="issues">
                  {unit.issues.map((issue) => (
                    <div className="issue" key={issue.id}>
                      <div className="issue-main">
                        <div>
                          <h4>{issue.issue}</h4>
                          <p>{issue.description}</p>
                        </div>

                        <span
                          className={`severity ${issue.severity.toLowerCase()}`}
                        >
                          {issue.severity}
                        </span>
                      </div>

                      <div className="issue-meta">
                        <span>
                          Condition: <strong>{issue.condition}</strong>
                        </span>

                        <span>
                          Visible: {issue.visible_items.join(", ")}
                        </span>
                      </div>

                      {issue.work_order && (
                        <div className="work-order">
                          <div>
                            <p className="eyebrow">WORK ORDER</p>
                            <h4>{issue.work_order.title}</h4>
                            <p>{issue.work_order.description}</p>

                            <small>
                              Recommended:{" "}
                              {issue.work_order.recommended_action}
                            </small>
                          </div>

                          <div className="work-actions">
                            <span className="draft">
                              {issue.work_order.status}
                            </span>

                            {issue.work_order.status === "DRAFT" &&
                              issue.work_order.id != null && (
                                <>
                                  <button
                                    className="accept-button"
                                    onClick={() =>
                                      handleWorkOrderDecision(
                                        issue.work_order!.id!,
                                        true,
                                      )
                                    }
                                  >
                                    Accept
                                  </button>

                                  <button
                                    className="reject-button"
                                    onClick={() =>
                                      handleWorkOrderDecision(
                                        issue.work_order!.id!,
                                        false,
                                      )
                                    }
                                  >
                                    Reject
                                  </button>
                                </>
                              )}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section className="card">
              <div className="card-header">
                <div>
                  <p className="eyebrow">AI ASSISTED MAINTENANCE</p>
                  <h3>Report an Issue</h3>
                </div>
              </div>

              <p className="muted">
                Upload a property photo to generate a draft issue and
                work order.
              </p>

              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={(event) =>
                  setPhoto(event.target.files?.[0] ?? null)
                }
              />

              <button
                className="primary-button"
                disabled={!photo || photoLoading}
                onClick={handleAnalyzePhoto}
              >
                {photoLoading ? "Analyzing..." : "Analyze Photo"}
              </button>

              {photoResult && (
                <div className="review-panel">
                  <p className="eyebrow">HUMAN REVIEW</p>
                  <h3>{photoResult.issue}</h3>
                  <p>{photoResult.description}</p>

                  <div className="review-grid">
                    <div>
                      <span>Severity</span>
                      <strong>{photoResult.severity}</strong>
                    </div>

                    <div>
                      <span>Condition</span>
                      <strong>{photoResult.condition}</strong>
                    </div>

                    <div>
                      <span>Visible Items</span>
                      <strong>
                        {photoResult.visible_items.join(", ")}
                      </strong>
                    </div>
                  </div>

                  {photoResult.work_order && (
                    <div className="draft-order">
                      <p className="eyebrow">DRAFT WORK ORDER</p>
                      <h4>{photoResult.work_order.title}</h4>
                      <p>{photoResult.work_order.description}</p>

                      <p>
                        <strong>Recommended action:</strong>{" "}
                        {photoResult.work_order.recommended_action}
                      </p>
                    </div>
                  )}

                  <div className="review-actions">
                    <button
                      className="accept-button"
                      onClick={handleAcceptIssue}
                    >
                      Accept &amp; Create Issue
                    </button>

                    <button
                      className="reject-button"
                      onClick={() => {
                        setPhotoResult(null);
                        setPhoto(null);
                      }}
                    >
                      Reject
                    </button>
                  </div>
                </div>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
