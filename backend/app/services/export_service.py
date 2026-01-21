import os
import shutil
import zipfile
import tempfile
from typing import Optional
from ..config_new import get_config
from ..services.simulation_manager import SimulationManager
from ..services.report_agent import ReportManager
from ..models.project import ProjectManager
from ..utils.logger import get_logger

logger = get_logger('multimo.services.export')

class ExportService:
    """
    Export Service
    Bundles all data related to a simulation into a zip file for download.
    """

    @classmethod
    def export_simulation_data(cls, simulation_id: str) -> Optional[str]:
        """
        Export all data for a simulation ID.
        
        Returns:
            Path to the temporary zip file, or None if failed.
        """
        temp_dir = tempfile.mkdtemp()
        zip_filename = f"multimo_export_{simulation_id}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                
                # 1. Export Simulation Data
                sim_manager = SimulationManager()
                sim_dir = sim_manager._get_simulation_dir(simulation_id)
                
                if os.path.exists(sim_dir):
                    logger.info(f"Exporting simulation data from {sim_dir}")
                    for root, dirs, files in os.walk(sim_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.join('simulation', os.path.relpath(file_path, sim_dir))
                            zipf.write(file_path, arcname)
                            
                            # Try to find project_id from state.json
                            if file == 'state.json':
                                try:
                                    import json
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        state = json.load(f)
                                        project_id = state.get('project_id')
                                        if project_id:
                                            # 2. Export Project Data
                                            cls._add_project_data(zipf, project_id)
                                except Exception as e:
                                    logger.warning(f"Failed to read project_id from state.json: {e}")

                # 3. Export Report Data
                # Find report associated with this simulation
                report_id = cls._find_report_id(simulation_id)
                if report_id:
                    report_folder = ReportManager._get_report_folder(report_id)
                    if os.path.exists(report_folder):
                        logger.info(f"Exporting report data from {report_folder}")
                        for root, dirs, files in os.walk(report_folder):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.join('report', os.path.relpath(file_path, report_folder))
                                zipf.write(file_path, arcname)

            return zip_path

        except Exception as e:
            logger.error(f"Export failed: {e}")
            shutil.rmtree(temp_dir) # Clean up on failure
            return None

    @classmethod
    def _add_project_data(cls, zipf: zipfile.ZipFile, project_id: str):
        """Helper to add project files to the zip"""
        project_dir = ProjectManager._get_project_dir(project_id)
        if os.path.exists(project_dir):
            logger.info(f"Exporting project data from {project_dir}")
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join('project', os.path.relpath(file_path, project_dir))
                    zipf.write(file_path, arcname)

    @classmethod
    def _find_report_id(cls, simulation_id: str) -> Optional[str]:
        """Find the latest report ID for a given simulation ID"""
        # This logic mimics _get_report_id_for_simulation in api/simulation.py
        # Ideally we should refactor to share this logic, but for now we duplicate slightly to avoid circular imports if api imports services
        # Actually, we can reuse ReportManager if it had this method, but it doesn't.
        # Let's inspect ReportManager directories.
        reports_dir = ReportManager.REPORTS_DIR
        if not os.path.exists(reports_dir):
            return None
        
        matching_reports = []
        import json
        for report_folder in os.listdir(reports_dir):
            report_path = os.path.join(reports_dir, report_folder)
            if not os.path.isdir(report_path):
                continue
            
            meta_file = os.path.join(report_path, "meta.json")
            if not os.path.exists(meta_file):
                continue
            
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                if meta.get("simulation_id") == simulation_id:
                    matching_reports.append(meta)
            except:
                continue
        
        if matching_reports:
            # Sort by created_at desc
            matching_reports.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return matching_reports[0].get("report_id")
        return None
