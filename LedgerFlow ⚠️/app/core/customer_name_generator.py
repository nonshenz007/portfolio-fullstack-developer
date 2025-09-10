import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import re

@dataclass
class CustomerProfile:
    """Complete customer profile with all details"""
    name: str
    company_name: Optional[str]
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    phone: str
    email: Optional[str]
    gst_number: Optional[str]
    vat_number: Optional[str]
    customer_type: str  # 'individual' or 'business'
    region: str

class CustomerNameGenerator:
    """
    Enhanced customer name generator with region-based realistic names and addresses
    
    Features:
    - Generic Indian names
    - South Indian Muslim names (Malabar style)
    - Bahrain Arabic names
    - Realistic addresses and phone numbers
    - Business name generation
    - GST/VAT number generation
    - Regional postal codes
    """
    
    # Indian name datasets
    INDIAN_NAMES = {
        'first_names': {
            'male': [
                'Amit', 'Raj', 'Vikram', 'Suresh', 'Ramesh', 'Deepak', 'Manoj', 'Sanjay',
                'Ravi', 'Anil', 'Vinod', 'Ajay', 'Rohit', 'Sachin', 'Pradeep', 'Ashok',
                'Rakesh', 'Mahesh', 'Dinesh', 'Rajesh', 'Kiran', 'Nitin', 'Sandeep', 'Vivek'
            ],
            'female': [
                'Priya', 'Sunita', 'Meena', 'Kavita', 'Rekha', 'Pooja', 'Neha', 'Ritu',
                'Anjali', 'Sushma', 'Geeta', 'Seema', 'Nisha', 'Rashmi', 'Shilpa', 'Vandana',
                'Kalpana', 'Madhuri', 'Usha', 'Lata', 'Sita', 'Radha', 'Kamala', 'Savita'
            ]
        },
        'surnames': [
            'Sharma', 'Gupta', 'Singh', 'Kumar', 'Patel', 'Shah', 'Jain', 'Agarwal',
            'Bansal', 'Mittal', 'Mehta', 'Chopra', 'Malhotra', 'Arora', 'Kapoor', 'Khanna',
            'Verma', 'Srivastava', 'Tiwari', 'Pandey', 'Mishra', 'Yadav', 'Thakur', 'Rao'
        ]
    }
    
    # South Indian Muslim names (Malabar style)
    SOUTH_MUSLIM_NAMES = {
        'first_names': {
            'male': [
                'Abdul Rahman', 'Mohammed', 'Yusuf', 'Ibrahim', 'Ismail', 'Rashid', 'Salim',
                'Hameed', 'Majeed', 'Jaleel', 'Kareem', 'Hakeem', 'Naseer', 'Basheer',
                'Muneer', 'Sameer', 'Shakir', 'Tahir', 'Umar', 'Zubair', 'Farid', 'Khalil'
            ],
            'female': [
                'Fathima', 'Ayesha', 'Khadija', 'Mariam', 'Zainab', 'Hafsa', 'Ruqaiya',
                'Safiya', 'Sumayya', 'Asma', 'Fatima', 'Aisha', 'Khadijah', 'Maryam',
                'Zaynab', 'Hafsah', 'Ruqayyah', 'Safiyyah', 'Sumayyah', 'Asma', 'Noor', 'Layla'
            ]
        },
        'surnames': [
            'Ali', 'Hassan', 'Hussein', 'Ahmad', 'Khan', 'Sheikh', 'Ansari', 'Qureshi',
            'Siddiqui', 'Farooqui', 'Usmani', 'Rizvi', 'Naqvi', 'Abidi', 'Zaidi', 'Kazmi',
            'Meer', 'Mirza', 'Baig', 'Beg', 'Pasha', 'Malik', 'Chowdhury', 'Mulla'
        ]
    }
    
    # Bahrain Arabic names
    BAHRAIN_ARABIC_NAMES = {
        'first_names': {
            'male': [
                'Ahmed', 'Mohammed', 'Ali', 'Hassan', 'Omar', 'Khalid', 'Youssef', 'Saeed',
                'Abdulla', 'Hamad', 'Nasser', 'Fahad', 'Majid', 'Tariq', 'Waleed', 'Saud',
                'Faisal', 'Rashid', 'Mansour', 'Adel', 'Jamal', 'Karim', 'Salman', 'Zayed'
            ],
            'female': [
                'Fatima', 'Mariam', 'Layla', 'Noor', 'Sara', 'Amina', 'Huda', 'Zahra',
                'Maha', 'Reem', 'Dina', 'Lina', 'Rana', 'Hala', 'Noura', 'Rima',
                'Salma', 'Wafa', 'Ghada', 'Nadia', 'Suha', 'Lara', 'Maya', 'Tala'
            ]
        },
        'surnames': [
            'Al Khalifa', 'Al Zayani', 'Al Farsi', 'Al Jalahma', 'Al Qassab', 'Al Sayed',
            'Al Mahmood', 'Al Ansari', 'Al Dosari', 'Al Mansoori', 'Al Thani', 'Al Rashid',
            'Al Sabah', 'Al Maktoum', 'Al Nahyan', 'Al Qasimi', 'Al Nuaimi', 'Al Shamsi',
            'Al Mazrouei', 'Al Kaabi', 'Al Blooshi', 'Al Hammadi', 'Al Suwaidi', 'Al Dhaheri'
        ]
    }
    
    # Business name patterns
    BUSINESS_PATTERNS = {
        'India': {
            'trading': [
                '{name} Traders', '{name} Trading Co.', '{name} Enterprises', '{name} & Co.',
                '{name} Trading Company', '{name} Commercial', '{name} Exports', '{name} Imports'
            ],
            'retail': [
                '{name} General Store', '{name} Mart', '{name} Super Market', '{name} Store',
                '{name} Retail', '{name} Shop', '{name} Emporium', '{name} Bazaar'
            ],
            'services': [
                '{name} Services', '{name} Solutions', '{name} Consultancy', '{name} Systems',
                '{name} Technologies', '{name} Infotech', '{name} Digital', '{name} Tech'
            ],
            'manufacturing': [
                '{name} Industries', '{name} Manufacturing', '{name} Products', '{name} Works',
                '{name} Mills', '{name} Factory', '{name} Production', '{name} Fabrication'
            ]
        },
        'Bahrain': {
            'trading': [
                '{name} Trading Co. W.L.L.', '{name} Commercial Est.', '{name} Trading Est.',
                '{name} International Trading', '{name} Gulf Trading', '{name} Middle East Trading'
            ],
            'retail': [
                '{name} Supermarket', '{name} Hypermarket', '{name} Store', '{name} Retail',
                '{name} Shopping Center', '{name} Market', '{name} Grocery', '{name} Mart'
            ],
            'services': [
                '{name} Services Co.', '{name} Consulting', '{name} Solutions', '{name} Group',
                '{name} Holdings', '{name} Management', '{name} Advisory', '{name} Consulting'
            ]
        }
    }
    
    # Address components
    ADDRESS_COMPONENTS = {
        'India': {
            'street_types': ['Street', 'Road', 'Lane', 'Colony', 'Nagar', 'Marg', 'Gali', 'Chowk'],
            'areas': [
                'Andheri', 'Bandra', 'Malad', 'Borivali', 'Thane', 'Pune', 'Nashik', 'Nagpur',
                'Sector 14', 'Sector 22', 'Model Town', 'Civil Lines', 'Cantonment', 'Old City',
                'New Town', 'Industrial Area', 'Commercial Complex', 'Market Area'
            ],
            'cities': [
                'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad',
                'Surat', 'Jaipur', 'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Thane', 'Bhopal',
                'Visakhapatnam', 'Pimpri', 'Patna', 'Vadodara', 'Ghaziabad', 'Ludhiana', 'Agra', 'Nashik'
            ],
            'states': [
                'Maharashtra', 'Karnataka', 'Tamil Nadu', 'Gujarat', 'Rajasthan', 'Uttar Pradesh',
                'West Bengal', 'Telangana', 'Andhra Pradesh', 'Kerala', 'Madhya Pradesh', 'Bihar',
                'Odisha', 'Punjab', 'Haryana', 'Assam', 'Jharkhand', 'Chhattisgarh'
            ]
        },
        'Bahrain': {
            'areas': [
                'Manama', 'Muharraq', 'Riffa', 'Hamad Town', 'Isa Town', 'Sitra', 'Tubli',
                'Budaiya', 'Jidhafs', 'Sanabis', 'Seef', 'Adliya', 'Juffair', 'Hoora',
                'Gudaibiya', 'Zinj', 'Mahooz', 'Salmaniya', 'Naim', 'Galali'
            ],
            'districts': [
                'Capital', 'Muharraq', 'Northern', 'Southern'
            ]
        }
    }
    
    # Phone number patterns
    PHONE_PATTERNS = {
        'India': {
            'mobile': '+91-{area}-{number}',
            'landline': '+91-{city}-{number}',
            'area_codes': ['98', '99', '97', '96', '95', '94', '93', '92', '91', '90'],
            'city_codes': ['22', '11', '80', '44', '33', '40', '20', '79', '141', '522']
        },
        'Bahrain': {
            'mobile': '+973-{number}',
            'landline': '+973-{number}',
            'mobile_prefixes': ['3', '6'],
            'landline_prefixes': ['1', '2', '4']
        }
    }
    
    def __init__(self):
        self.generated_names = set()
        self.generated_companies = set()
    
    def generate_customer_profile(self, 
                                region: str = 'generic_indian',
                                customer_type: str = 'mixed',
                                invoice_type: str = 'gst') -> CustomerProfile:
        """
        Generate complete customer profile
        
        Args:
            region: 'generic_indian', 'south_muslim', 'bahrain_arabic'
            customer_type: 'individual', 'business', 'mixed'
            invoice_type: 'gst', 'vat', 'cash'
            
        Returns:
            CustomerProfile with all details
        """
        # Determine customer type
        if customer_type == 'mixed':
            is_business = random.choice([True, False])
        else:
            is_business = customer_type == 'business'
        
        # Generate name
        name = self._generate_name(region)
        
        # Generate company name (if business)
        company_name = None
        if is_business:
            company_name = self._generate_company_name(region, name)
        
        # Generate address
        address_info = self._generate_address(region)
        
        # Generate phone
        phone = self._generate_phone(region)
        
        # Generate email
        email = self._generate_email(name, company_name)
        
        # Generate tax numbers
        gst_number = None
        vat_number = None
        
        if invoice_type == 'gst' and is_business:
            gst_number = self._generate_gst_number(address_info['state'])
        elif invoice_type == 'vat' and is_business:
            vat_number = self._generate_vat_number()
        
        return CustomerProfile(
            name=name,
            company_name=company_name,
            address=address_info['address'],
            city=address_info['city'],
            state=address_info['state'],
            country=address_info['country'],
            postal_code=address_info['postal_code'],
            phone=phone,
            email=email,
            gst_number=gst_number,
            vat_number=vat_number,
            customer_type='business' if is_business else 'individual',
            region=region
        )
    
    def generate_batch_customers(self, 
                               count: int,
                               region: str = 'generic_indian',
                               customer_type: str = 'mixed',
                               invoice_type: str = 'gst',
                               return_rate: float = 0.3) -> List[CustomerProfile]:
        """
        Generate batch of customers with return customer logic
        
        Args:
            count: Number of customers to generate
            region: Region type
            customer_type: Customer type
            invoice_type: Invoice type
            return_rate: Probability of returning existing customer
            
        Returns:
            List of CustomerProfile objects
        """
        customers = []
        existing_customers = []
        
        for i in range(count):
            # Decide if this should be a return customer
            if existing_customers and random.random() < return_rate:
                # Return existing customer
                customer = random.choice(existing_customers)
                customers.append(customer)
            else:
                # Generate new customer
                customer = self.generate_customer_profile(region, customer_type, invoice_type)
                customers.append(customer)
                existing_customers.append(customer)
        
        return customers
    
    def _generate_name(self, region: str) -> str:
        """Generate name based on region"""
        if region == 'generic_indian':
            return self._generate_indian_name()
        elif region == 'south_muslim':
            return self._generate_south_muslim_name()
        elif region == 'bahrain_arabic':
            return self._generate_bahrain_arabic_name()
        else:
            return self._generate_indian_name()  # Default
    
    def _generate_indian_name(self) -> str:
        """Generate generic Indian name"""
        gender = random.choice(['male', 'female'])
        first_name = random.choice(self.INDIAN_NAMES['first_names'][gender])
        surname = random.choice(self.INDIAN_NAMES['surnames'])
        
        # Sometimes add middle name
        if random.random() < 0.3:
            middle_name = random.choice(['Kumar', 'Devi', 'Lal', 'Bai', 'Chand'])
            return f"{first_name} {middle_name} {surname}"
        
        return f"{first_name} {surname}"
    
    def _generate_south_muslim_name(self) -> str:
        """Generate South Indian Muslim name"""
        gender = random.choice(['male', 'female'])
        first_name = random.choice(self.SOUTH_MUSLIM_NAMES['first_names'][gender])
        surname = random.choice(self.SOUTH_MUSLIM_NAMES['surnames'])
        
        # Sometimes add honorific
        if random.random() < 0.2:
            if gender == 'male':
                honorific = random.choice(['Haji', 'Maulana', 'Ustad'])
                return f"{honorific} {first_name} {surname}"
            else:
                honorific = random.choice(['Hajjah', 'Begum'])
                return f"{first_name} {surname} {honorific}"
        
        return f"{first_name} {surname}"
    
    def _generate_bahrain_arabic_name(self) -> str:
        """Generate Bahrain Arabic name"""
        gender = random.choice(['male', 'female'])
        first_name = random.choice(self.BAHRAIN_ARABIC_NAMES['first_names'][gender])
        surname = random.choice(self.BAHRAIN_ARABIC_NAMES['surnames'])
        
        # Sometimes add father's name
        if random.random() < 0.4:
            father_name = random.choice(self.BAHRAIN_ARABIC_NAMES['first_names']['male'])
            return f"{first_name} {father_name} {surname}"
        
        return f"{first_name} {surname}"
    
    def _generate_company_name(self, region: str, owner_name: str) -> str:
        """Generate company name based on region"""
        country = 'India' if region in ['generic_indian', 'south_muslim'] else 'Bahrain'
        
        # Extract first name for company name
        first_name = owner_name.split()[0]
        
        # Choose business type
        business_types = list(self.BUSINESS_PATTERNS[country].keys())
        business_type = random.choice(business_types)
        
        # Choose pattern
        patterns = self.BUSINESS_PATTERNS[country][business_type]
        pattern = random.choice(patterns)
        
        # Sometimes use surname instead of first name
        if random.random() < 0.3 and len(owner_name.split()) > 1:
            name_for_company = owner_name.split()[-1]  # Last name
        else:
            name_for_company = first_name
        
        company_name = pattern.format(name=name_for_company)
        
        # Ensure uniqueness
        counter = 1
        original_name = company_name
        while company_name in self.generated_companies:
            company_name = f"{original_name} {counter}"
            counter += 1
        
        self.generated_companies.add(company_name)
        return company_name
    
    def _generate_address(self, region: str) -> Dict[str, str]:
        """Generate address based on region"""
        if region in ['generic_indian', 'south_muslim']:
            return self._generate_indian_address()
        else:
            return self._generate_bahrain_address()
    
    def _generate_indian_address(self) -> Dict[str, str]:
        """Generate Indian address"""
        # Building number
        building_no = random.randint(1, 999)
        
        # Street
        street_type = random.choice(self.ADDRESS_COMPONENTS['India']['street_types'])
        street_name = random.choice(['MG', 'Gandhi', 'Nehru', 'Station', 'Main', 'Church', 'Market'])
        street = f"{street_name} {street_type}"
        
        # Area
        area = random.choice(self.ADDRESS_COMPONENTS['India']['areas'])
        
        # City and state
        city = random.choice(self.ADDRESS_COMPONENTS['India']['cities'])
        state = random.choice(self.ADDRESS_COMPONENTS['India']['states'])
        
        # Postal code (6 digits)
        postal_code = f"{random.randint(100000, 999999)}"
        
        # Full address
        address = f"{building_no}, {street}, {area}"
        
        return {
            'address': address,
            'city': city,
            'state': state,
            'country': 'India',
            'postal_code': postal_code
        }
    
    def _generate_bahrain_address(self) -> Dict[str, str]:
        """Generate Bahrain address"""
        # Building number
        building_no = random.randint(1, 999)
        
        # Road/Street
        road_no = random.randint(1, 50)
        
        # Block
        block_no = random.randint(100, 999)
        
        # Area
        area = random.choice(self.ADDRESS_COMPONENTS['Bahrain']['areas'])
        
        # District
        district = random.choice(self.ADDRESS_COMPONENTS['Bahrain']['districts'])
        
        # Postal code (3 or 4 digits)
        postal_code = f"{random.randint(100, 9999)}"
        
        # Full address
        address = f"Building {building_no}, Road {road_no}, Block {block_no}"
        
        return {
            'address': address,
            'city': area,
            'state': f"{district} Governorate",
            'country': 'Bahrain',
            'postal_code': postal_code
        }
    
    def _generate_phone(self, region: str) -> str:
        """Generate phone number based on region"""
        if region in ['generic_indian', 'south_muslim']:
            return self._generate_indian_phone()
        else:
            return self._generate_bahrain_phone()
    
    def _generate_indian_phone(self) -> str:
        """Generate Indian phone number"""
        # Mobile or landline
        if random.random() < 0.8:  # 80% mobile
            area_code = random.choice(self.PHONE_PATTERNS['India']['area_codes'])
            number = f"{random.randint(1000000, 9999999)}"
            return f"+91-{area_code}{number}"
        else:  # Landline
            city_code = random.choice(self.PHONE_PATTERNS['India']['city_codes'])
            number = f"{random.randint(1000000, 9999999)}"
            return f"+91-{city_code}-{number}"
    
    def _generate_bahrain_phone(self) -> str:
        """Generate Bahrain phone number"""
        if random.random() < 0.7:  # 70% mobile
            prefix = random.choice(self.PHONE_PATTERNS['Bahrain']['mobile_prefixes'])
            number = f"{prefix}{random.randint(1000000, 9999999)}"
            return f"+973-{number}"
        else:  # Landline
            prefix = random.choice(self.PHONE_PATTERNS['Bahrain']['landline_prefixes'])
            number = f"{prefix}{random.randint(100000, 999999)}"
            return f"+973-{number}"
    
    def _generate_email(self, name: str, company_name: Optional[str]) -> Optional[str]:
        """Generate email address"""
        if random.random() < 0.6:  # 60% chance of having email
            # Clean name for email
            clean_name = re.sub(r'[^a-zA-Z\s]', '', name.lower())
            name_parts = clean_name.split()
            
            if company_name and random.random() < 0.4:
                # Use company domain
                domain_part = re.sub(r'[^a-zA-Z]', '', company_name.lower().split()[0])
                domain = f"{domain_part}.com"
            else:
                # Use common domains
                domain = random.choice(['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'])
            
            # Generate email username
            if len(name_parts) >= 2:
                username = f"{name_parts[0]}.{name_parts[1]}"
            else:
                username = name_parts[0]
            
            # Add numbers sometimes
            if random.random() < 0.3:
                username += str(random.randint(1, 999))
            
            return f"{username}@{domain}"
        
        return None
    
    def _generate_gst_number(self, state: str) -> str:
        """Generate realistic GST number"""
        # State codes (simplified)
        state_codes = {
            'Maharashtra': '27', 'Karnataka': '29', 'Tamil Nadu': '33',
            'Gujarat': '24', 'Rajasthan': '08', 'Uttar Pradesh': '09',
            'West Bengal': '19', 'Telangana': '36', 'Andhra Pradesh': '37',
            'Kerala': '32', 'Madhya Pradesh': '23', 'Bihar': '10'
        }
        
        state_code = state_codes.get(state, '27')  # Default to Maharashtra
        
        # Generate PAN-like part (5 letters + 4 digits + 1 letter)
        letters1 = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))
        digits = ''.join(random.choices('0123456789', k=4))
        letter2 = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        
        # Entity code and check digit
        entity_code = random.choice(['1', '2', '3', '4'])
        check_digit = random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        
        return f"{state_code}{letters1}{digits}{letter2}{entity_code}Z{check_digit}"
    
    def _generate_vat_number(self) -> str:
        """Generate Bahrain VAT number"""
        # Bahrain VAT numbers are typically 9 digits
        return f"{random.randint(100000000, 999999999)}"
    
    def get_region_statistics(self, customers: List[CustomerProfile]) -> Dict[str, Any]:
        """Get statistics about generated customers"""
        stats = {
            'total_customers': len(customers),
            'by_region': {},
            'by_type': {'individual': 0, 'business': 0},
            'by_country': {},
            'with_gst': 0,
            'with_vat': 0,
            'with_email': 0
        }
        
        for customer in customers:
            # By region
            if customer.region not in stats['by_region']:
                stats['by_region'][customer.region] = 0
            stats['by_region'][customer.region] += 1
            
            # By type
            stats['by_type'][customer.customer_type] += 1
            
            # By country
            if customer.country not in stats['by_country']:
                stats['by_country'][customer.country] = 0
            stats['by_country'][customer.country] += 1
            
            # Tax numbers
            if customer.gst_number:
                stats['with_gst'] += 1
            if customer.vat_number:
                stats['with_vat'] += 1
            
            # Email
            if customer.email:
                stats['with_email'] += 1
        
        return stats 