"""
Reminders service for handling payment reminders.
"""

from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from app.logging import get_logger
from app.models_simple import PaymentReminderStatus
from app.utils.i18n import get_translation
from app.bot.services.repo_sync import PaymentReminderRepository

logger = get_logger(__name__)


class RemindersService:
    """Service for handling payment reminders."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_due_reminders(self) -> List:
        """
        Get payment reminders that are due.
        
        Returns:
            List of PaymentReminder objects
        """
        return PaymentReminderRepository.get_pending_reminders(self.session)
    
    def mark_reminder_sent(self, reminder) -> None:
        """
        Mark reminder as sent.
        
        Args:
            reminder: PaymentReminder object
        """
        PaymentReminderRepository.update_status(
            self.session,
            reminder,
            PaymentReminderStatus.SENT
        )
    
    def create_reminder(
        self,
        student_id: int,
        due_at: datetime
    ):
        """
        Create a new payment reminder.
        
        Args:
            student_id: Student ID
            due_at: Due date for payment
            
        Returns:
            PaymentReminder object
        """
        return PaymentReminderRepository.create(
            self.session,
            student_id=student_id,
            due_at=due_at,
            status=PaymentReminderStatus.PENDING
        )
    
    def process_due_reminders(self) -> dict:
        """
        Process all due reminders and return statistics.
        
        Returns:
            Dictionary with processing statistics
        """
        reminders = self.get_due_reminders()
        
        stats = {
            "total": len(reminders),
            "processed": 0,
            "errors": 0
        }
        
        for reminder in reminders:
            try:
                # Here you would send the actual reminder message
                # For now, we just mark it as sent
                self.mark_reminder_sent(reminder)
                stats["processed"] += 1
                
                logger.info(
                    "Payment reminder processed",
                    reminder_id=reminder.id,
                    student_id=reminder.student_id
                )
            except Exception as e:
                stats["errors"] += 1
                logger.error(
                    "Failed to process payment reminder",
                    reminder_id=reminder.id,
                    error=str(e)
                )
        
        return stats
