import requests
from config import BSCSCAN_API_KEY

class CryptoGuardian:
    def __init__(self):
        self.api_key = BSCSCAN_API_KEY
        self.base_url = 'https://api.bscscan.com/api'
    
    async def scan_contract(self, contract_address):
        try:
            url = f'{self.base_url}?module=contract&action=getsourcecode&address={contract_address}&apikey={self.api_key}'
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data['status'] != '1':
                return {'success': False, 'error': 'Contract not found'}
            
            source_code = data['result'][0]['SourceCode']
            issues = []
            risk_level = 'Low'
            
            if not source_code:
                return {'success': False, 'error': 'No source code'}
            
            if 'transfer' in source_code.lower() and 'require' in source_code.lower():
                issues.append('️ Has transfer restrictions')
                risk_level = 'Medium'
            
            if 'owner' in source_code.lower() or 'onlyowner' in source_code.lower():
                issues.append('⚠️ Has owner functions')
            
            if 'mint' in source_code.lower():
                issues.append('🔴 Has mint function')
                risk_level = 'High'
            
            if 'pause' in source_code.lower():
                issues.append('⚠️ Can be paused by owner')
            
            issues.append('ℹ️ Verify liquidity on Dextools')
            
            return {
                'success': True,
                'address': contract_address,
                'risk_level': risk_level,
                'issues': issues,
                'verified': 'Yes' if data['result'][0]['ABI'] else 'No'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
