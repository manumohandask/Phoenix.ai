"""
Quick test script to verify Azure DevOps connectivity
Run this to test your PAT and repository access before using the full UI
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.azure_devops_client import AzureDevOpsClient


async def test_azure_devops_connection():
    """Test Azure DevOps API connection"""
    
    print("=" * 60)
    print("Azure DevOps Connection Test")
    print("=" * 60)
    
    # Get credentials
    print("\nEnter your Azure DevOps details:")
    organization = input("Organization (e.g., hrblock-ca): ").strip()
    project = input("Project (e.g., TPS Cloud): ").strip()
    repository = input("Repository (e.g., HRB-TPSC-QA-EnterpriseAutomation): ").strip()
    pat = input("Personal Access Token: ").strip()
    
    if not all([organization, project, repository, pat]):
        print("❌ Error: All fields are required")
        return
    
    print("\n" + "=" * 60)
    print("Testing connection...")
    print("=" * 60)
    
    try:
        # Create client
        client = AzureDevOpsClient(organization, project, pat, repository)
        print(f"\n✓ Client created successfully")
        print(f"  Base URL: {client.base_url}")
        
        # Test 1: Fetch pull requests
        print("\n📋 Test 1: Fetching pull requests...")
        prs = await client.list_pull_requests()
        print(f"✅ Success! Found {len(prs)} pull request(s)")
        
        if prs:
            print("\n   Latest PRs:")
            for pr in prs[:5]:  # Show first 5
                print(f"   - PR #{pr['pullRequestId']}: {pr['title'][:60]}")
                print(f"     Status: {pr['status']}, Author: {pr['createdBy']['displayName']}")
        else:
            print("   No pull requests found in this repository")
        
        # Test 2: Get details for first PR (if available)
        if prs:
            pr_id = prs[0]['pullRequestId']
            print(f"\n📝 Test 2: Fetching details for PR #{pr_id}...")
            pr_details = await client.get_pr_details(pr_id)
            print(f"✅ Success! Retrieved PR details")
            print(f"   Title: {pr_details['pr']['title']}")
            print(f"   Commits: {len(pr_details['commits'])}")
            print(f"   File Changes: {len(pr_details['changes'])}")
            print(f"   Work Items: {len(pr_details['workitems'])}")
            
            if pr_details['changes']:
                print(f"\n   Sample file changes:")
                for change in pr_details['changes'][:5]:
                    if isinstance(change.get('item'), dict):
                        path = change['item'].get('path', 'Unknown')
                    else:
                        path = change.get('path', 'Unknown')
                    change_type = change.get('changeType', 'edit')
                    print(f"   - {change_type}: {path}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour Azure DevOps connection is working correctly.")
        print("You can now use the PR Testing Agent in the WebUI.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify your Personal Access Token is valid")
        print("2. Check that you have access to the repository")
        print("3. Ensure organization/project/repository names are correct")
        print("4. Make sure your PAT has 'Code (Read)' and 'Pull Request Threads (Read & Write)' permissions")
        print("\nFor more help, see docs/AZURE_DEVOPS_SETUP.md")
        return


if __name__ == "__main__":
    asyncio.run(test_azure_devops_connection())
