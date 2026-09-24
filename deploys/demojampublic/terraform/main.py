"""Demonstrate a public JAM stack."""

from helicopyter.cloudflare import jam
from stacks.base import provide

provide('cloudflare/cloudflare', '5.25.0')
jam('demojampublic.example.com/')
