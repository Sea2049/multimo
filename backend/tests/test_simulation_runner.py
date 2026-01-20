import os
import json
import unittest
from unittest.mock import MagicMock, patch, mock_open
from app.services.simulation_runner import SimulationRunner, SimulationRunState, RunnerStatus

class TestSimulationRunner(unittest.TestCase):
    def setUp(self):
        # Reset class level variables
        SimulationRunner._run_states = {}
        SimulationRunner._processes = {}
        SimulationRunner._action_queues = {}
        SimulationRunner._monitor_threads = {}
        SimulationRunner._stdout_files = {}
        SimulationRunner._stderr_files = {}
        SimulationRunner._graph_memory_enabled = {}

    @patch('app.services.simulation_runner.os.path.exists')
    @patch('app.services.simulation_runner.open', new_callable=mock_open)
    def test_get_run_state_not_exists(self, mock_file, mock_exists):
        mock_exists.return_value = False
        state = SimulationRunner.get_run_state("test_sim_id")
        self.assertIsNone(state)

    @patch('app.services.simulation_runner.os.path.exists')
    @patch('app.services.simulation_runner.open', new_callable=mock_open)
    def test_get_run_state_exists(self, mock_file, mock_exists):
        mock_exists.return_value = True
        mock_data = {
            "simulation_id": "test_sim_id",
            "runner_status": "running",
            "current_round": 5
        }
        mock_file.return_value.read.return_value = json.dumps(mock_data)
        
        # Mock json.load to return the dict directly
        with patch('json.load', return_value=mock_data):
            state = SimulationRunner.get_run_state("test_sim_id")
            
        self.assertIsNotNone(state)
        self.assertEqual(state.simulation_id, "test_sim_id")
        self.assertEqual(state.runner_status, RunnerStatus.RUNNING)
        self.assertEqual(state.current_round, 5)

    @patch('app.services.simulation_runner.subprocess.Popen')
    @patch('app.services.simulation_runner.os.path.exists')
    @patch('app.services.simulation_runner.open', new_callable=mock_open)
    @patch('app.services.simulation_runner.threading.Thread')
    def test_start_simulation(self, mock_thread, mock_file, mock_exists, mock_popen):
        # Setup mocks
        mock_exists.return_value = True # Config exists
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        # Mock config file content
        config_data = {
            "time_config": {
                "total_simulation_hours": 24,
                "minutes_per_round": 60
            }
        }
        
        # We need to handle multiple open calls (config, log file, state file)
        # This is tricky with mock_open, so we'll just mock json.load
        with patch('json.load', return_value=config_data):
            with patch('json.dump'): # Mock saving state
                state = SimulationRunner.start_simulation("test_sim_id", platform="twitter")
        
        self.assertEqual(state.simulation_id, "test_sim_id")
        self.assertEqual(state.runner_status, RunnerStatus.RUNNING)
        self.assertEqual(state.process_pid, 12345)
        self.assertTrue(state.twitter_running)
        self.assertFalse(state.reddit_running)
        
        # Verify process started
        mock_popen.assert_called_once()
        
        # Verify monitor thread started
        mock_thread.assert_called_once()

    @patch('app.services.simulation_runner.SimulationRunner.get_run_state')
    @patch('app.services.simulation_runner.SimulationRunner._save_run_state')
    def test_stop_simulation(self, mock_save, mock_get_state):
        # Setup mock state
        mock_state = MagicMock(spec=SimulationRunState)
        mock_state.simulation_id = "test_sim_id"
        mock_state.runner_status = RunnerStatus.RUNNING
        mock_get_state.return_value = mock_state
        
        # Setup mock process
        mock_process = MagicMock()
        mock_process.poll.return_value = None # Running
        SimulationRunner._processes["test_sim_id"] = mock_process
        
        # Run stop
        with patch('app.services.simulation_runner.SimulationRunner._terminate_process') as mock_terminate:
            SimulationRunner.stop_simulation("test_sim_id")
            mock_terminate.assert_called_once_with(mock_process, "test_sim_id")
            
        self.assertEqual(mock_state.runner_status, RunnerStatus.STOPPED)
        self.assertFalse(mock_state.twitter_running)
        self.assertFalse(mock_state.reddit_running)

if __name__ == '__main__':
    unittest.main()
