"""
Reminders service for handling payment reminders.
"""

from datetime import datetime, timedelta
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.logging import get_logger
from app.models import PaymentReminderStatus
from app.utils.i18n import get_translation
from app.bot.services.repo import PaymentReminderRepository

logger = get_logger(__name__)


class RemindersService:
    """Service for handling payment reminders."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_due_reminders(self) -> List:
        """
        Get payment reminders that are due.
        
        Returns:
            List of PaymentReminder objects
        """
        return await PaymentReminderRepository.get_pending_reminders(self.session)
    
    async def mark_reminder_sent(self, reminder) -> None:
        """
        Mark reminder as sent.
        
        Args:
            reminder: PaymentReminder object
        """
        await PaymentReminderRepository.update_status(
            self.session,
            reminder,
            PaymentReminderStatus.SENT
        )
    
    async def create_reminder(
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
        return await PaymentReminderRepository.create(
            self.session,
            student_id=student_id,
            due_at=due_at,
            status=PaymentReminderStatus.PENDING
        )
    
    async def process_due_reminders(self) -> dict:
        """
        Process all due reminders and return statistics.
        
        Returns:
            Dictionary with processing statistics
        """
        reminders = await self.get_due_reminders()
        
        stats = {
            "total": len(reminders),
            "processed": 0,
            "errors": 0
        }
        
        for reminder in reminders:
            try:
                # Here you would send the actual reminder message
                # For now, we just mark it as sent
                await self.mark_reminder_sent(reminder)
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
