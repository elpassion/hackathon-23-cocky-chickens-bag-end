provider "aws" {
  region = "eu-central-1"
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnet_ids" "default" {
  vpc_id = data.aws_vpc.default.id
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_key_pair" "api" {
  key_name   = "zrgh-chicken"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAEAQDWr4LAnW6P1t8Tcw4r9UMpVxT8LSunmOOMVQ4WGuoIiLbtAAVblCSFjY+oS3vJBRg5nFx7ZY9OI5WTb3riBDwabctxj0GiVkrz7hv3UwaYtQ238uIHHVPXWiMJdUOfEDj83BTUefv/npN157U8Q6texvJvy8L0xsPcnOC4siQSrDc8ZAw1zJ+JhAE6EMPwQDBdkT1OXkoHeOBhyJ1mVdglvUdraz07c6r4tBtIdZsgNGEnpfkFVU761zBg8xcrEkRl/Qnpd3HpYJC/pQ+5ZlUTl89/PzEMnV6D7tUi5hISy7N9ReOHR14/XuNnPcIJL0S9C1vTjGBah7sSE3PbYhi9cGixXpjCWcSVDkyED7pJQNwDTROK5XDK2q41GauHJMpuOQd825armoGfzrFqDDrD71TlVmpOVT+l4jZdoOU9Q9IldxNFXCDpt0xdyDW4kT/okK7yetZNvxxt1MK0sU9eZCbHJelh8ByEIneeyOrvVg2yvNXOcP9i0MWn2ZLXvUq3e9h2zW3NUIN4xry1VEhCQk4f92uDso3ABA5hIPVxI4zL/wXl0XwA4t480YeMFd3bMOB3vxqk/vOsEnxyrwfgkzJaXmh5DeP3btpqDh1+JY5qrfwoRxD6X1hKX+4VfeQz/nHr1kRJliKEtSQ0Z1dH2RnJrBA5pJWVfHgxgD018pEHdZkCpaGFm9RlEE3uK7iSlnhOQdxzADyntjJ8pGl6q2R1GnC7IVMY683bNJ4J5Wjx8SW8eKl9fH17uiyJrGNKI0kN/tYnofCphVPRN5II+2eUPb8f4ZofMPf/SbAzsDGxsZfYDv+HBdee5neIu39NExbXSqZUhmSmBnYzcAJxlUCVCzWOXYuPeNFwUPxdTBUBpw4ozyAQUCPzk4MQUt2/QihwxHJ68GiERsMBBmShFH3nMiLCtu2MQOuHc0RAZyRt2woUXF6blstJtcalOeRJUaU0O6DnkJUrOT2gKown6Kp2HlW4okg2yhyvD+s2lDgEB9X/Tx35lpYAbVNa5FWnOZXTeFmIYClJoERYrXkpC16dRjXEn150U98ts5xCv3IbZAGw7Cx9UCeF41O8Xk+oCJHuJVu92ip9QCJcPgI9SX8ajvzYDWVqONwVcTdJrajDnAINjNsGcz41/Gjopi7Z9cEErekCx1VakbFIMBMZZ8hDfQrf3htpdM9ApDDCBFr0EVyUt2AfiuEOaYw/SnymB6g6aHX8btV4NcZDWOW5uOiSelszSC+Gh/WG8gfyzguyfb2Ux/sqbQOg3Y+PoZmckJBw5MUCYGUMo6RdBJ7eXYq1dBW2679zdVjOfBIkDRUuGtjJPMX2XeK2Cks++rYKrY3/xuFmSLxhOXXaQhpN jakub.andrzejewski@eplassion.pl"
}

module "api_label" {
  source  = "cloudposse/label/terraform"
  version = "~> 0.6.0"

  stage     = "prod"
  namespace = "chicken"
  name      = "api"
}


module "bastion_sg" {
  source  = "terraform-aws-modules/security-group/aws//modules/ssh"
  version = "~> 3.18.0"

  name = "chicken-ssh"
  vpc_id = data.aws_vpc.default.id

  ingress_cidr_blocks = ["0.0.0.0/0"]
}

module "http_sg" {
  source  = "terraform-aws-modules/security-group/aws//modules/http-80"
  version = "~> 3.18.0"

  name = "chicken-ssh"
  vpc_id = data.aws_vpc.default.id

  ingress_cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_instance" "api" {

  ami                    = data.aws_ami.ubuntu.id
  subnet_id              = tolist(data.aws_subnet_ids.default.ids)[0]
  instance_type          = "t3.micro"
  key_name               = aws_key_pair.api.key_name
  vpc_security_group_ids = [module.bastion_sg.this_security_group_id, module.http_sg.this_security_group_id]

  root_block_device {
    volume_type = "gp2"
    volume_size = 20
  }

  tags = module.api_label.tags

  lifecycle {
    ignore_changes = [ami]
  }
}

data "aws_route53_zone" "this" {
  zone_id = "Z05952891IKMIM2HQTURO"
}

resource "aws_route53_record" "api" {
  name = "api"
  type = "A"
  zone_id = data.aws_route53_zone.this.id

  ttl = 300
  records = [aws_instance.api.public_ip]
}