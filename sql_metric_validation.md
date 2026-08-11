# SQL-Based Insight Validation

This document describes the process for validating metric consistency between SQL view definitions and Python calculations.

## Purpose

Ensure SQL and Python compute the same business metrics. Catch drift early by comparing both layers side-by-side and flagging discrepancies.

## Validation Approach

1. Compute metrics in SQL using the official views.
2. Compute the same metrics in Python using the same business logic.
3. Compare the results with a tolerance threshold.
4. Investigate and fix any discrepancies.

## Example Metrics

- active_users
- churn_rate
- total_revenue
- average_transaction_value

## Example Report

- active_users: SQL=1200, Python=1188, diff=1.0%
- revenue: SQL=50000.00, Python=49950.00, diff=0.10%

If differences exceed the configured tolerance, the validation report flags them for review.

## Tolerance Guidelines

- Use a small numeric tolerance for counts and ratios.
- Use relative tolerance for larger monetary metrics.
- Document any expected differences explicitly.
