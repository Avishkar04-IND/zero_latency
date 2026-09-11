from backend.app.models.organization import Organization
from backend.app.models.branch import Branch
from backend.app.models.user import User
from backend.app.core.security import get_password_hash, create_access_token


def test_branch_management_and_rbac(client, db_session):
    # Setup Organization 1 and Org Admin
    org1 = Organization(name="Apex Laboratories", licence_no="LIC-APEX-01", contact_email="apex@test.com")
    db_session.add(org1)
    db_session.flush()

    admin1 = User(
        name="Apex Admin",
        email="admin@apex.com",
        password_hash=get_password_hash("AdminPass123"),
        role="ORG_ADMIN",
        organization_id=org1.id,
        is_active=True
    )
    operator1 = User(
        name="Apex Operator",
        email="operator@apex.com",
        password_hash=get_password_hash("OpPass123"),
        role="OPERATOR",
        organization_id=org1.id,
        is_active=True
    )
    db_session.add_all([admin1, operator1])
    db_session.commit()

    token_admin1 = create_access_token(admin1.id, extra_claims={"role": admin1.role, "org_id": org1.id})
    token_op1 = create_access_token(operator1.id, extra_claims={"role": operator1.role, "org_id": org1.id})

    headers_admin = {"Authorization": f"Bearer {token_admin1}"}
    headers_op = {"Authorization": f"Bearer {token_op1}"}

    # 1. ORG_ADMIN creates a new branch
    create_res = client.post("/api/v1/branches", json={
        "name": "Mumbai Formulation Facility",
        "code": "BR-MUM-01",
        "city": "Mumbai",
        "state": "Maharashtra",
        "contact_phone": "+91-22-12345678"
    }, headers=headers_admin)
    assert create_res.status_code == 201
    branch_data = create_res.json()
    assert branch_data["name"] == "Mumbai Formulation Facility"
    assert branch_data["organization_id"] == org1.id
    assert branch_data["code"] == "BR-MUM-01"
    branch_id = branch_data["id"]

    # 2. OPERATOR attempts to create a branch -> 403 Forbidden
    op_create_res = client.post("/api/v1/branches", json={
        "name": "Unauthorized Facility",
        "code": "BR-FAIL-01"
    }, headers=headers_op)
    assert op_create_res.status_code == 403

    # 3. List branches -> should contain newly created branch
    list_res = client.get("/api/v1/branches", headers=headers_admin)
    assert list_res.status_code == 200
    branches = list_res.json()
    assert len(branches) == 1
    assert branches[0]["code"] == "BR-MUM-01"

    # 4. Get branch by ID
    get_res = client.get(f"/api/v1/branches/{branch_id}", headers=headers_op)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Mumbai Formulation Facility"

    # 5. Patch branch details
    patch_res = client.patch(f"/api/v1/branches/{branch_id}", json={
        "contact_email": "mumbai.unit@apex.com"
    }, headers=headers_admin)
    assert patch_res.status_code == 200
    assert patch_res.json()["contact_email"] == "mumbai.unit@apex.com"

    # 6. Test GET /api/v1/organizations/me
    me_res = client.get("/api/v1/organizations/me", headers=headers_admin)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["name"] == "Apex Laboratories"
    assert len(me_data["branches"]) == 1
    assert me_data["branches"][0]["id"] == branch_id


def test_branch_tenant_isolation(client, db_session):
    # Setup two separate organizations
    orgA = Organization(name="Company A", licence_no="LIC-A", contact_email="a@test.com")
    orgB = Organization(name="Company B", licence_no="LIC-B", contact_email="b@test.com")
    db_session.add_all([orgA, orgB])
    db_session.flush()

    branchA = Branch(organization_id=orgA.id, name="Plant A", code="BR-A1")
    db_session.add(branchA)
    db_session.flush()

    userB = User(
        name="User B",
        email="admin@companyb.com",
        password_hash=get_password_hash("Pass123"),
        role="ORG_ADMIN",
        organization_id=orgB.id,
        is_active=True
    )
    db_session.add(userB)
    db_session.commit()

    tokenB = create_access_token(userB.id, extra_claims={"role": userB.role, "org_id": orgB.id})
    headersB = {"Authorization": f"Bearer {tokenB}"}

    # User from Org B attempts to access Branch of Org A -> 403 Forbidden
    res_get = client.get(f"/api/v1/branches/{branchA.id}", headers=headersB)
    assert res_get.status_code == 403

    # User from Org B attempts to patch Branch of Org A -> 403 Forbidden
    res_patch = client.patch(f"/api/v1/branches/{branchA.id}", json={"name": "Tampered"}, headers=headersB)
    assert res_patch.status_code == 403

    # Listing branches for Org B should return empty list (not Org A's branch)
    res_list = client.get("/api/v1/branches", headers=headersB)
    assert res_list.status_code == 200
    assert len(res_list.json()) == 0
