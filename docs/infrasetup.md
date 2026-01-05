# Infrastructure Requirements: Static Site with API Backend

## Architecture

```
[User] → [Cloudflare] → [S3 static site]
                     → [EC2 backend API]
```

## Prerequisites

- AWS CLI configured with valid credentials
- OpenTofu installed
- S3 state bucket exists: `danalv-site-tfstate`
- Domain registered and managed by Cloudflare
- SSH key pair (create if not exists)

## AWS Resources

### Networking

| Resource | Configuration |
|----------|---------------|
| VPC | CIDR `10.0.0.0/24` |
| Internet Gateway | Attached to VPC |
| Public Subnet | CIDR `10.0.0.0/24`, AZ `us-east-1a`, auto-assign public IP |
| Route Table | Default route `0.0.0.0/0` → IGW |
| Route Table Association | Associate subnet to route table |

### Compute

| Resource | Configuration |
|----------|---------------|
| Security Group | Ingress: SSH (22) from operator IP, HTTP (80) from `0.0.0.0/0`, HTTPS (443) from `0.0.0.0/0`, backend port from `0.0.0.0/0`. Egress: all |
| EC2 Instance | Type: TBD, AMI: Amazon Linux 2023 or Ubuntu 24.04, Subnet: public, Security Group: above |
| Elastic IP | Associated to EC2 instance |

### Storage

| Resource | Configuration |
|----------|---------------|
| S3 Bucket | Name: must match domain exactly (e.g., `www.example.com`), Website hosting enabled, Index document: `index.html`, Error document: `index.html` or `404.html`, Public access: enabled via bucket policy |

## Required Input Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `aws_region` | AWS region | `us-east-1` |
| `project_name` | Project identifier for tagging | `danalv-site` |
| `environment` | Environment name | `dev` |
| `vpc_cidr` | VPC CIDR block | `10.0.0.0/24` |
| `az` | Availability zone | `us-east-1a` |
| `domain_name` | Domain for S3 bucket name | `danalv.com` |
| `instance_type` | EC2 instance type | `t3.micro` |
| `backend_port` | Port API listens on | `8080` |

## File Structure

```
infra/
├── main.tf           # Provider, backend config
├── variables.tf      # Variable declarations
├── outputs.tf        # Output values
├── terraform.tfvars  # Variable values
├── vpc.tf            # VPC, subnet, IGW, route table
├── ec2.tf            # Security group, EC2 instance, Elastic IP
├── s3.tf             # S3 bucket with website config
```

## Resource Naming Convention

Pattern: `{project_name}-{environment}-{resource_type}`

Examples:
- `danalv-site-dev-vpc`
- `danalv-site-dev-public-subnet`
- `danalv-site-dev-ec2`
- `danalv-site-dev-sg`

## Tagging Standard

All resources tagged with:

```hcl
tags = {
  Project     = var.project_name
  Environment = var.environment
  ManagedBy   = "OpenTofu"
}
```

## Backend Configuration

```hcl
backend "s3" {
  bucket       = "danalv-site-tfstate"
  key          = "dev/terraform.tfstate"
  region       = "us-east-1"
  use_lockfile = true
}
```

## Outputs

| Output | Value |
|--------|-------|
| `vpc_id` | VPC ID |
| `public_subnet_id` | Public subnet ID |
| `ec2_public_ip` | Elastic IP address |
| `ec2_instance_id` | EC2 instance ID |
| `s3_bucket_name` | S3 bucket name |
| `s3_website_endpoint` | S3 website URL |

## Post-Apply: Cloudflare DNS Configuration

| Record | Type | Target | Proxy |
|--------|------|--------|-------|
| `@` or `www` | CNAME | S3 website endpoint | Enabled |
| `api` | A | EC2 Elastic IP | Enabled |

## Execution Sequence

1. `tofu init`
2. `tofu plan`
3. `tofu apply`
4. Configure Cloudflare DNS records using outputs
5. Deploy frontend to S3
6. Deploy backend to EC2
