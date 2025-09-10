import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import calendar
from dataclasses import dataclass

@dataclass
class BusinessSchedule:
    """Defines business operating schedule"""
    working_days: List[int]  # 0=Monday, 6=Sunday
    working_hours: Tuple[int, int]  # (start_hour, end_hour)
    peak_hours: List[Tuple[int, int]]  # Peak business hours
    lunch_break: Optional[Tuple[int, int]]  # Lunch break hours
    seasonal_factors: Dict[int, float]  # Month -> factor (1.0 = normal)

class TimeFlowEngine:
    """
    TimeFlowEngine™ - Generates realistic invoice timestamps with human-like patterns
    
    Features:
    - Weekday clustering (more invoices on weekdays)
    - Holiday gaps (no invoices on holidays)
    - Business hour concentration
    - Seasonal variations
    - Lunch break dips
    - Weekend patterns for different business types
    """
    
    # Indian holidays (approximate dates)
    INDIAN_HOLIDAYS = {
        1: [1, 26],  # New Year, Republic Day
        3: [8],      # Holi (approximate)
        4: [14],     # Ram Navami (approximate)
        8: [15],     # Independence Day
        10: [2, 20], # Gandhi Jayanti, Dussehra (approximate)
        11: [7],     # Diwali (approximate)
        12: [25]     # Christmas
    }
    
    # Bahrain holidays
    BAHRAIN_HOLIDAYS = {
        1: [1],      # New Year
        5: [1],      # Labour Day
        12: [16, 17] # National Day, Accession Day
    }
    
    # Business schedule presets
    BUSINESS_SCHEDULES = {
        'retail_shop': BusinessSchedule(
            working_days=[0, 1, 2, 3, 4, 5],  # Mon-Sat
            working_hours=(9, 21),
            peak_hours=[(11, 13), (17, 19)],
            lunch_break=(13, 14),
            seasonal_factors={10: 1.3, 11: 1.5, 12: 1.4, 1: 0.8, 2: 0.9}
        ),
        'distributor': BusinessSchedule(
            working_days=[0, 1, 2, 3, 4, 5],  # Mon-Sat
            working_hours=(8, 18),
            peak_hours=[(9, 11), (15, 17)],
            lunch_break=(12, 13),
            seasonal_factors={3: 1.2, 4: 1.1, 10: 1.3, 11: 1.4}
        ),
        'exporter': BusinessSchedule(
            working_days=[0, 1, 2, 3, 4],  # Mon-Fri
            working_hours=(9, 17),
            peak_hours=[(10, 12), (14, 16)],
            lunch_break=(12, 13),
            seasonal_factors={1: 1.1, 2: 1.2, 3: 1.3, 11: 1.2, 12: 1.1}
        ),
        'pharmacy': BusinessSchedule(
            working_days=[0, 1, 2, 3, 4, 5, 6],  # All days
            working_hours=(8, 22),
            peak_hours=[(9, 11), (18, 20)],
            lunch_break=None,
            seasonal_factors={6: 1.2, 7: 1.1, 12: 1.3, 1: 1.1}
        ),
        'it_service': BusinessSchedule(
            working_days=[0, 1, 2, 3, 4],  # Mon-Fri
            working_hours=(9, 18),
            peak_hours=[(10, 12), (14, 17)],
            lunch_break=(12, 13),
            seasonal_factors={3: 1.2, 9: 1.1, 10: 1.1, 11: 1.1}
        )
    }
    
    def __init__(self, business_style: str = 'retail_shop', country: str = 'India'):
        self.business_style = business_style
        self.country = country
        self.schedule = self.BUSINESS_SCHEDULES.get(business_style, self.BUSINESS_SCHEDULES['retail_shop'])
        self.holidays = self.INDIAN_HOLIDAYS if country == 'India' else self.BAHRAIN_HOLIDAYS
        
    def generate_invoice_timestamps(self, 
                                  count: int, 
                                  date_range: Tuple[datetime, datetime],
                                  reality_buffer: float = 0.85,
                                  believability_stress: float = 0.15) -> List[datetime]:
        """
        Generate realistic invoice timestamps
        
        Args:
            count: Number of timestamps to generate
            date_range: (start_date, end_date) tuple
            reality_buffer: How closely to stick to realistic patterns (0-1)
            believability_stress: Amount of randomness to add (0-1)
        
        Returns:
            List of datetime objects sorted chronologically
        """
        start_date, end_date = date_range
        
        # Generate base date distribution
        dates = self._generate_base_dates(count, start_date, end_date)
        
        # Apply business schedule filtering
        dates = self._apply_business_schedule(dates, reality_buffer)
        
        # Add time components
        timestamps = self._add_time_components(dates, reality_buffer, believability_stress)
        
        # Apply seasonal adjustments
        timestamps = self._apply_seasonal_adjustments(timestamps)
        
        # Sort chronologically
        timestamps.sort()
        
        return timestamps
    
    def _generate_base_dates(self, count: int, start_date: datetime, end_date: datetime) -> List[datetime]:
        """Generate base dates with weekday preference"""
        dates = []
        total_days = (end_date - start_date).days
        
        # Create weighted date distribution
        date_weights = []
        current_date = start_date
        
        for _ in range(total_days + 1):
            weight = self._get_date_weight(current_date)
            date_weights.append(weight)
            current_date += timedelta(days=1)
        
        # Normalize weights
        total_weight = sum(date_weights)
        if total_weight > 0:
            date_weights = [w / total_weight for w in date_weights]
        else:
            date_weights = [1.0 / len(date_weights)] * len(date_weights)
        
        # Sample dates based on weights
        for _ in range(count):
            day_index = np.random.choice(len(date_weights), p=date_weights)
            selected_date = start_date + timedelta(days=day_index)
            dates.append(selected_date)
        
        return dates
    
    def _get_date_weight(self, date: datetime) -> float:
        """Get weight for a specific date based on business patterns"""
        weight = 1.0
        
        # Weekday preference
        weekday = date.weekday()
        if weekday in self.schedule.working_days:
            weight *= 2.0
        else:
            weight *= 0.1  # Very few invoices on non-working days
        
        # Holiday check
        if self._is_holiday(date):
            weight *= 0.05  # Almost no invoices on holidays
        
        # Month-end preference (more invoices near month end)
        day_of_month = date.day
        days_in_month = calendar.monthrange(date.year, date.month)[1]
        
        if day_of_month > days_in_month - 7:  # Last week of month
            weight *= 1.3
        elif day_of_month <= 3:  # First few days
            weight *= 1.1
        
        # Seasonal factors
        month_factor = self.schedule.seasonal_factors.get(date.month, 1.0)
        weight *= month_factor
        
        return weight
    
    def _is_holiday(self, date: datetime) -> bool:
        """Check if date is a holiday"""
        month_holidays = self.holidays.get(date.month, [])
        return date.day in month_holidays
    
    def _apply_business_schedule(self, dates: List[datetime], reality_buffer: float) -> List[datetime]:
        """Filter dates based on business schedule"""
        filtered_dates = []
        
        for date in dates:
            # Check if it's a working day
            if date.weekday() in self.schedule.working_days:
                filtered_dates.append(date)
            elif random.random() < (1 - reality_buffer) * 0.2:  # Sometimes work on off days
                filtered_dates.append(date)
        
        # If we lost too many dates, add some back
        if len(filtered_dates) < len(dates) * 0.8:
            needed = len(dates) - len(filtered_dates)
            for _ in range(needed):
                # Add random working days
                base_date = random.choice(dates)
                while base_date.weekday() not in self.schedule.working_days:
                    base_date += timedelta(days=1)
                filtered_dates.append(base_date)
        
        return filtered_dates
    
    def _add_time_components(self, dates: List[datetime], reality_buffer: float, believability_stress: float) -> List[datetime]:
        """Add realistic time components to dates"""
        timestamps = []
        
        for date in dates:
            # Get business hours for this date
            start_hour, end_hour = self.schedule.working_hours
            
            # Check if it's a peak hour
            is_peak_time = random.random() < reality_buffer
            
            if is_peak_time and self.schedule.peak_hours:
                # Select from peak hours
                peak_start, peak_end = random.choice(self.schedule.peak_hours)
                hour = random.randint(peak_start, peak_end - 1)
            else:
                # Select from regular business hours
                hour = random.randint(start_hour, end_hour - 1)
            
            # Avoid lunch break
            if self.schedule.lunch_break:
                lunch_start, lunch_end = self.schedule.lunch_break
                if lunch_start <= hour < lunch_end and random.random() < reality_buffer:
                    # Move to before or after lunch
                    if random.random() < 0.5:
                        hour = lunch_start - 1
                    else:
                        hour = lunch_end
                    hour = max(start_hour, min(end_hour - 1, hour))
            
            # Add randomness for believability stress
            if random.random() < believability_stress:
                # Sometimes create outliers
                if random.random() < 0.3:
                    hour = random.randint(6, 23)  # Very early or late
            
            # Generate minutes with clustering around common times
            minute_clusters = [0, 15, 30, 45]  # Common appointment times
            if random.random() < reality_buffer:
                minute = random.choice(minute_clusters)
            else:
                minute = random.randint(0, 59)
            
            # Add some seconds for uniqueness
            second = random.randint(0, 59)
            
            timestamp = date.replace(hour=hour, minute=minute, second=second)
            timestamps.append(timestamp)
        
        return timestamps
    
    def _apply_seasonal_adjustments(self, timestamps: List[datetime]) -> List[datetime]:
        """Apply seasonal business pattern adjustments"""
        # This is a placeholder for more sophisticated seasonal adjustments
        # For now, we rely on the seasonal factors in date generation
        return timestamps
    
    def get_business_day_distribution(self, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """Get distribution of business days in the date range"""
        distribution = {
            'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0,
            'Friday': 0, 'Saturday': 0, 'Sunday': 0
        }
        
        current_date = start_date
        while current_date <= end_date:
            day_name = current_date.strftime('%A')
            if current_date.weekday() in self.schedule.working_days:
                distribution[day_name] += 1
            current_date += timedelta(days=1)
        
        return distribution
    
    def estimate_invoice_capacity(self, date_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Estimate realistic invoice capacity for the date range"""
        start_date, end_date = date_range
        total_days = (end_date - start_date).days + 1
        
        # Count working days
        working_days = 0
        holiday_days = 0
        
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() in self.schedule.working_days:
                if not self._is_holiday(current_date):
                    working_days += 1
                else:
                    holiday_days += 1
            current_date += timedelta(days=1)
        
        # Estimate capacity based on business style
        daily_capacity = {
            'retail_shop': 15,
            'distributor': 8,
            'exporter': 3,
            'pharmacy': 25,
            'it_service': 5
        }
        
        base_capacity = daily_capacity.get(self.business_style, 10)
        estimated_capacity = working_days * base_capacity
        
        return {
            'total_days': total_days,
            'working_days': working_days,
            'holiday_days': holiday_days,
            'estimated_daily_capacity': base_capacity,
            'estimated_total_capacity': estimated_capacity,
            'recommended_max_invoices': int(estimated_capacity * 0.8)  # 80% of capacity
        } 