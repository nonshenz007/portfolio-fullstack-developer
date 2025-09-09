"""
Asynchronous Processing Engine for VeriDoc

Provides non-blocking processing capabilities with progress tracking,
cancellation support, and resource management for production use.
"""

import asyncio
import threading
import concurrent.futures
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum
import time
import logging
from pathlib import Path
import queue

from core.error_handler import get_error_handler, ErrorCategory, ErrorSeverity
from config.production_config import get_config


class ProcessingState(Enum):
    """States for async processing operations."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class ProcessingTask:
    """Represents an asynchronous processing task."""
    task_id: str
    operation: str
    input_data: Any
    callback: Optional[Callable] = None
    progress_callback: Optional[Callable] = None
    state: ProcessingState = ProcessingState.PENDING
    progress: float = 0.0
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    @property
    def duration(self) -> Optional[float]:
        """Get task duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return time.time() - self.start_time
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            'task_id': self.task_id,
            'operation': self.operation,
            'state': self.state.value,
            'progress': self.progress,
            'result': self.result,
            'error': self.error,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'metadata': self.metadata
        }


class AsyncProcessor:
    """
    Production-ready asynchronous processor with thread pool management,
    queue handling, and resource monitoring.
    """

    def __init__(self, max_workers: int = None, queue_size: int = None):
        self.logger = logging.getLogger(__name__)
        self.config = get_config()

        # Configuration
        self.max_workers = max_workers or self.config.performance.max_worker_threads
        self.queue_size = queue_size or self.config.performance.queue_size_limit

        # Thread pool and event loop
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix="veridoc-worker"
        )
        self.event_loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.loop_thread.start()

        # Task management
        self.tasks: Dict[str, ProcessingTask] = {}
        self.task_queue = queue.Queue(maxsize=self.queue_size)
        self.cancelled_tasks = set()

        # Monitoring
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'cancelled_tasks': 0,
            'avg_processing_time': 0.0,
            'active_workers': 0
        }

        # Control flags
        self.running = True
        self.shutdown_event = threading.Event()

        # Start queue processor
        self.queue_processor = threading.Thread(target=self._process_queue, daemon=True)
        self.queue_processor.start()

        self.logger.info(f"AsyncProcessor initialized with {self.max_workers} workers")

    def _run_event_loop(self):
        """Run the asyncio event loop in a separate thread."""
        asyncio.set_event_loop(self.event_loop)
        try:
            self.event_loop.run_forever()
        except Exception as e:
            self.logger.error(f"Event loop error: {e}")

    def _process_queue(self):
        """Process tasks from the queue."""
        while self.running and not self.shutdown_event.is_set():
            try:
                # Get task from queue with timeout
                task = self.task_queue.get(timeout=1.0)

                if task.task_id in self.cancelled_tasks:
                    self.cancelled_tasks.remove(task.task_id)
                    task.state = ProcessingState.CANCELLED
                    self._notify_callback(task)
                    continue

                # Submit task to thread pool
                future = self.executor.submit(self._execute_task, task)
                future.add_done_callback(lambda f, t=task: self._handle_task_completion(f, t))

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Queue processing error: {e}")

    def _execute_task(self, task: ProcessingTask) -> Any:
        """Execute a processing task."""
        try:
            task.start_time = time.time()
            task.state = ProcessingState.RUNNING

            # Update progress
            if task.progress_callback:
                task.progress_callback(0.1, "Starting processing...")

            # Here you would implement the actual processing logic
            # For now, we'll simulate processing
            result = self._simulate_processing(task)

            task.progress = 1.0
            task.state = ProcessingState.COMPLETED
            task.end_time = time.time()

            if task.progress_callback:
                task.progress_callback(1.0, "Processing completed")

            return result

        except Exception as e:
            task.state = ProcessingState.FAILED
            task.error = str(e)
            task.end_time = time.time()

            error_handler = get_error_handler()
            error_handler.handle_error(
                error_handler.create_error(
                    f"Task {task.task_id} failed: {e}",
                    ErrorCategory.PROCESSING,
                    ErrorSeverity.MEDIUM,
                    "TASK_EXECUTION_FAILED"
                )
            )

            raise e

    def _simulate_processing(self, task: ProcessingTask) -> Any:
        """Simulate processing for demonstration - replace with actual logic."""
        import time
        import random

        # Simulate different processing times
        if task.operation == "face_detection":
            processing_time = random.uniform(0.5, 2.0)
        elif task.operation == "validation":
            processing_time = random.uniform(0.1, 0.5)
        elif task.operation == "batch_processing":
            processing_time = random.uniform(5.0, 15.0)
        else:
            processing_time = random.uniform(1.0, 3.0)

        steps = 10
        for i in range(steps):
            if task.task_id in self.cancelled_tasks:
                raise asyncio.CancelledError("Task was cancelled")

            time.sleep(processing_time / steps)

            progress = (i + 1) / steps
            if task.progress_callback:
                task.progress_callback(progress, f"Step {i + 1} of {steps}")

        return f"Processed {task.operation} for {task.input_data}"

    def _handle_task_completion(self, future: concurrent.futures.Future, task: ProcessingTask):
        """Handle completion of a task."""
        try:
            if future.cancelled():
                task.state = ProcessingState.CANCELLED
                self.stats['cancelled_tasks'] += 1
            elif future.exception():
                task.state = ProcessingState.FAILED
                task.error = str(future.exception())
                self.stats['failed_tasks'] += 1
            else:
                task.result = future.result()
                task.state = ProcessingState.COMPLETED
                self.stats['completed_tasks'] += 1

                # Update average processing time
                if task.duration:
                    total_time = self.stats['avg_processing_time'] * self.stats['total_tasks']
                    total_time += task.duration
                    self.stats['total_tasks'] += 1
                    self.stats['avg_processing_time'] = total_time / self.stats['total_tasks']

            # Notify callback
            self._notify_callback(task)

        except Exception as e:
            self.logger.error(f"Task completion handling error: {e}")

    def _notify_callback(self, task: ProcessingTask):
        """Notify task completion callback."""
        if task.callback:
            try:
                task.callback(task)
            except Exception as e:
                self.logger.error(f"Callback error for task {task.task_id}: {e}")

    async def submit_task_async(self, operation: str, input_data: Any,
                              callback: Optional[Callable] = None,
                              progress_callback: Optional[Callable] = None,
                              metadata: Optional[Dict[str, Any]] = None) -> str:
        """Submit a task for asynchronous processing."""
        task_id = f"{operation}_{int(time.time() * 1000)}_{hash(str(input_data)) % 10000}"

        task = ProcessingTask(
            task_id=task_id,
            operation=operation,
            input_data=input_data,
            callback=callback,
            progress_callback=progress_callback,
            metadata=metadata or {}
        )

        self.tasks[task_id] = task
        self.stats['total_tasks'] += 1

        # Add to queue
        try:
            self.task_queue.put_nowait(task)
            self.logger.debug(f"Task {task_id} submitted to queue")
        except queue.Full:
            task.state = ProcessingState.FAILED
            task.error = "Task queue is full"
            self.stats['failed_tasks'] += 1

            error_handler = get_error_handler()
            error_handler.handle_error(
                error_handler.create_error(
                    f"Task queue full, cannot submit {operation}",
                    ErrorCategory.PROCESSING,
                    ErrorSeverity.MEDIUM,
                    "QUEUE_FULL"
                )
            )

        return task_id

    def submit_task(self, operation: str, input_data: Any,
                   callback: Optional[Callable] = None,
                   progress_callback: Optional[Callable] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Synchronous wrapper for submit_task_async."""
        future = asyncio.run_coroutine_threadsafe(
            self.submit_task_async(operation, input_data, callback, progress_callback, metadata),
            self.event_loop
        )
        return future.result()

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.state == ProcessingState.RUNNING:
                self.cancelled_tasks.add(task_id)
                self.logger.info(f"Task {task_id} marked for cancellation")
                return True
        return False

    def get_task_status(self, task_id: str) -> Optional[ProcessingTask]:
        """Get the status of a task."""
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[ProcessingTask]:
        """Get all tasks."""
        return list(self.tasks.values())

    def get_active_tasks(self) -> List[ProcessingTask]:
        """Get currently active tasks."""
        return [task for task in self.tasks.values()
                if task.state in [ProcessingState.PENDING, ProcessingState.RUNNING]]

    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics."""
        stats = self.stats.copy()
        stats['queue_size'] = self.task_queue.qsize()
        stats['active_workers'] = len([t for t in self.tasks.values()
                                     if t.state == ProcessingState.RUNNING])
        return stats

    def shutdown(self, timeout: float = 30.0):
        """Shutdown the async processor gracefully."""
        self.logger.info("Shutting down AsyncProcessor...")

        self.running = False
        self.shutdown_event.set()

        # Cancel all pending tasks
        for task_id, task in self.tasks.items():
            if task.state in [ProcessingState.PENDING, ProcessingState.RUNNING]:
                self.cancel_task(task_id)

        # Wait for queue processor to finish
        if self.queue_processor.is_alive():
            self.queue_processor.join(timeout=timeout)

        # Shutdown thread pool
        self.executor.shutdown(wait=True, timeout=timeout)

        # Stop event loop
        if self.event_loop.is_running():
            self.event_loop.call_soon_threadsafe(self.event_loop.stop)

        if self.loop_thread.is_alive():
            self.loop_thread.join(timeout=timeout)

        self.logger.info("AsyncProcessor shutdown complete")


class ProcessingScheduler:
    """
    Advanced scheduler for managing processing workflows and dependencies.
    """

    def __init__(self, processor: AsyncProcessor):
        self.processor = processor
        self.workflows: Dict[str, List[ProcessingTask]] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self.workflow_callbacks: Dict[str, Callable] = {}

    def create_workflow(self, workflow_id: str, tasks: List[ProcessingTask],
                       dependencies: Optional[Dict[str, List[str]]] = None,
                       callback: Optional[Callable] = None) -> str:
        """Create a processing workflow with dependencies."""
        self.workflows[workflow_id] = tasks
        self.dependencies[workflow_id] = dependencies or {}
        if callback:
            self.workflow_callbacks[workflow_id] = callback

        # Submit initial tasks (those with no dependencies)
        for task in tasks:
            if task.task_id not in self.dependencies.get(workflow_id, []):
                self.processor.submit_task(
                    task.operation,
                    task.input_data,
                    lambda t, wf=workflow_id: self._handle_workflow_task_completion(wf, t),
                    task.progress_callback,
                    task.metadata
                )

        return workflow_id

    def _handle_workflow_task_completion(self, workflow_id: str, task: ProcessingTask):
        """Handle completion of a workflow task and submit dependent tasks."""
        if workflow_id not in self.workflows:
            return

        # Check if any dependent tasks can now be submitted
        workflow_deps = self.dependencies.get(workflow_id, {})

        for dependent_task_id, dependencies in workflow_deps.items():
            if task.task_id in dependencies:
                # Check if all dependencies are completed
                all_completed = True
                for dep_id in dependencies:
                    dep_task = next((t for t in self.workflows[workflow_id]
                                   if t.task_id == dep_id), None)
                    if dep_task and dep_task.state != ProcessingState.COMPLETED:
                        all_completed = False
                        break

                if all_completed:
                    # Submit the dependent task
                    dependent_task = next((t for t in self.workflows[workflow_id]
                                         if t.task_id == dependent_task_id), None)
                    if dependent_task:
                        self.processor.submit_task(
                            dependent_task.operation,
                            dependent_task.input_data,
                            lambda t, wf=workflow_id: self._handle_workflow_task_completion(wf, t),
                            dependent_task.progress_callback,
                            dependent_task.metadata
                        )

        # Check if workflow is complete
        all_completed = all(t.state == ProcessingState.COMPLETED
                          for t in self.workflows[workflow_id])

        if all_completed and workflow_id in self.workflow_callbacks:
            self.workflow_callbacks[workflow_id](self.workflows[workflow_id])


# Global processor instance
_async_processor: Optional[AsyncProcessor] = None


def get_async_processor() -> AsyncProcessor:
    """Get the global async processor instance."""
    global _async_processor
    if _async_processor is None:
        _async_processor = AsyncProcessor()
    return _async_processor


def shutdown_async_processor():
    """Shutdown the global async processor."""
    global _async_processor
    if _async_processor:
        _async_processor.shutdown()
        _async_processor = None
