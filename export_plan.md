# Export Plan for MiroFish Data

## 1. Export Scope
We want to bundle and export all data related to a simulation project, including:
- **Project Metadata**: `project.json` (includes ontology, original file names, simulation requirements)
- **Extracted Text**: `extracted_text.txt`
- **Graph Data**: Zep graph data (we need to fetch this from Zep, or just export the graph structure if cached. Since we can't easily export Zep's internal state to a file without API calls, we might skip full graph DB dump for now and focus on the ontology and the interaction logs which implicitly contain the graph updates).
- **Simulation Configuration**: `state.json` in simulation folder.
- **Simulation Logs**: `simulation.log`
- **Agent Actions**: `twitter/actions.jsonl` and `reddit/actions.jsonl` (raw interaction logs)
- **Generated Report**: `full_report.md` (if exists)

## 2. API Design
We will add a new endpoint in `backend/app/api/simulation.py` (or a new `export.py`):

**`GET /api/simulation/<simulation_id>/export`**

- **Function**: Bundles all relevant files into a ZIP archive.
- **Input**: `simulation_id`
- **Output**: Downloadable ZIP file named `mirofish_export_<simulation_id>.zip`

## 3. Implementation Steps

### Backend
1.  **Define `ExportService` in `backend/app/services/export_service.py`**:
    -   Method `export_simulation_data(simulation_id)`
    -   Locate project directory (via `simulation_id` -> `project_id` link in `state.json` or metadata)
    -   Locate simulation directory.
    -   Locate report directory (via `_get_report_id_for_simulation`).
    -   Create a temporary ZIP file.
    -   Add `project.json` and `extracted_text.txt` from project dir.
    -   Add all files from simulation dir (excluding large/unnecessary binaries if any, mainly logs and jsonls).
    -   Add `full_report.md` from report dir.
    -   Return path to ZIP.

2.  **Add API route in `backend/app/api/simulation.py`**:
    -   Call `ExportService`.
    -   Use `send_file` to return the ZIP.

### Frontend
1.  **Add Export Button**:
    -   In `SimulationRunView.vue` (monitor page) or `ReportView.vue` (result page).
    -   Add a button "Export Full Data" (导出完整数据).
    -   On click, trigger `window.open` or download action for the export API.

## 4. Specific File Paths (Recap)
- **Projects**: `backend/uploads/projects/<project_id>/`
- **Simulations**: `backend/uploads/simulations/<simulation_id>/`
- **Reports**: `backend/uploads/reports/<report_id>/`

We need to link `simulation_id` back to `project_id`. The `SimulationState` in `backend/app/services/simulation_manager.py` likely stores `project_id`. Let's verify `SimulationState` structure in `state.json`.

(Self-correction: I saw `to_dict` in `SimulationState` but didn't see the full definition. I'll assume it links them or I can find the project via the simulation folder content or metadata).

## 5. Execution Plan
1.  Create `backend/app/services/export_service.py`.
2.  Update `backend/app/api/simulation.py`.
3.  Restart Backend.
4.  Update Frontend `ReportView.vue` to include the button.
