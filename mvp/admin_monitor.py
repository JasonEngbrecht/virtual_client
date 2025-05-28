"""
Admin Monitor Dashboard - MVP Enhanced

Allows administrators to:
1. View active sessions in real-time
2. Monitor token usage and costs today  
3. Basic system metrics with manual/auto refresh
4. Usage graphs showing token trends over time
5. Error log viewer for debugging
6. Service health status monitoring

Part of the MVP to ensure comprehensive system monitoring.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
from pathlib import Path
import time
import pandas as pd

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from mvp.utils import (
    setup_page_config,
    show_info_message,
    show_error_message,
    show_success_message,
    initialize_session_state,
    get_database_connection,
    format_cost,
    format_tokens
)

from backend.services.session_service import session_service
from backend.services.anthropic_service import get_anthropic_service
from sqlalchemy import func


def fetch_admin_metrics() -> Dict[str, Any]:
    """
    Fetch key admin metrics from the database.
    
    Returns:
        Dictionary with admin metrics
    """
    metrics = {
        'active_sessions': 0,
        'tokens_today': 0,
        'cost_today': 0.0,
        'total_sessions': 0,
        'error': None
    }
    
    db = None
    try:
        db = get_database_connection()
        
        # Get count of active sessions
        metrics['active_sessions'] = session_service.count(
            db=db,
            status='active'
        )
        
        # Get total sessions (all time)
        metrics['total_sessions'] = session_service.count(db=db)
        
        # Get today's date range (midnight to now)
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now()
        
        # Get sessions started today for token/cost aggregation
        from backend.models.session import SessionDB
        today_sessions = db.query(SessionDB).filter(
            SessionDB.started_at >= today_start,
            SessionDB.started_at <= today_end
        ).all()
        
        # Aggregate tokens and costs from today's sessions
        metrics['tokens_today'] = sum(session.total_tokens or 0 for session in today_sessions)
        metrics['cost_today'] = sum(session.estimated_cost or 0.0 for session in today_sessions)
        
        return metrics
        
    except Exception as e:
        metrics['error'] = str(e)
        return metrics
    finally:
        if db:
            db.close()


def display_admin_metrics():
    """
    Display the main admin metrics dashboard.
    """
    st.subheader("📊 System Metrics")
    
    # Fetch metrics
    metrics = fetch_admin_metrics()
    
    if metrics['error']:
        show_error_message(f"Error fetching metrics: {metrics['error']}")
        return
    
    # Display key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🔴 Active Sessions",
            value=metrics['active_sessions']
        )
    
    with col2:
        st.metric(
            label="🪙 Tokens Today",
            value=format_tokens(metrics['tokens_today'])
        )
    
    with col3:
        st.metric(
            label="💰 Cost Today",
            value=format_cost(metrics['cost_today'])
        )
    
    with col4:
        st.metric(
            label="📈 Total Sessions",
            value=metrics['total_sessions']
        )
    
    # Additional info section
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"**Active Sessions:** Sessions currently in progress\n"
            f"**Tokens Today:** Total tokens used since midnight\n"
            f"**Cost Today:** Estimated cost for today's usage"
        )
    
    with col2:
        # Simple cost analysis
        if metrics['tokens_today'] > 0:
            cost_per_1k_tokens = (metrics['cost_today'] / metrics['tokens_today']) * 1000
        else:
            cost_per_1k_tokens = 0.0
        
        completion_rate = (
            (metrics['total_sessions'] - metrics['active_sessions']) / max(metrics['total_sessions'], 1) * 100
        ) if metrics['total_sessions'] > 0 else 0.0
        
        st.info(
            f"**Analysis:**\n\n"
            f"**Cost per 1K tokens:** {format_cost(cost_per_1k_tokens)}\n"
            f"**Completion rate:** {completion_rate:.1f}%\n"
            f"**Avg cost/session:** {format_cost(metrics['cost_today'] / max(metrics['total_sessions'], 1))}"
        )


def display_session_overview():
    """
    Display detailed session overview for admin monitoring.
    """
    st.subheader("🔍 Session Overview")
    
    db = None
    try:
        db = get_database_connection()
        
        # Get recent active sessions
        active_sessions = session_service.get_multi(
            db=db,
            status='active',
            limit=10
        )
        
        if not active_sessions:
            show_info_message("No active sessions at the moment.")
            return
        
        st.write(f"**Currently Active Sessions ({len(active_sessions)}):**")
        
        # Display active sessions in a table format
        for session in active_sessions:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**Session:** {session.id[:12]}...")
                    st.caption(f"Student: {session.student_id}")
                
                with col2:
                    st.write(f"**Client:** {session.client_profile_id[:12]}...")
                    duration = datetime.now() - session.started_at
                    duration_minutes = int(duration.total_seconds() // 60)
                    st.caption(f"Duration: {duration_minutes} min")
                
                with col3:
                    st.write(f"**Tokens:** {format_tokens(session.total_tokens or 0)}")
                    st.caption(f"Cost: {format_cost(session.estimated_cost or 0.0)}")
                
                with col4:
                    st.write(f"🟢 Active")
                    st.caption(f"Started: {session.started_at.strftime('%H:%M')}")
                
                st.divider()
        
        # Show button to view more if there are many active sessions
        if len(active_sessions) >= 10:
            total_active = session_service.count(db=db, status='active')
            if total_active > 10:
                st.info(f"Showing 10 of {total_active} active sessions. Use database queries for detailed analysis.")
    
    except Exception as e:
        show_error_message(f"Error loading session overview: {str(e)}")
    finally:
        if db:
            db.close()


def fetch_usage_timeline() -> pd.DataFrame:
    """
    Fetch hourly token usage for the last 24 hours.
    
    Returns:
        DataFrame with hourly token usage data
    """
    db = None
    try:
        db = get_database_connection()
        
        # Get 24 hours ago
        now = datetime.now()
        hours_ago_24 = now - timedelta(hours=24)
        
        # Get sessions from last 24 hours
        from backend.models.session import SessionDB
        recent_sessions = db.query(SessionDB).filter(
            SessionDB.started_at >= hours_ago_24
        ).all()
        
        # Create hourly buckets
        usage_data = []
        for i in range(24):
            hour_start = hours_ago_24 + timedelta(hours=i)
            hour_end = hour_start + timedelta(hours=1)
            
            # Find sessions in this hour
            hour_tokens = sum(
                session.total_tokens or 0 
                for session in recent_sessions 
                if hour_start <= session.started_at < hour_end
            )
            hour_cost = sum(
                session.estimated_cost or 0.0 
                for session in recent_sessions 
                if hour_start <= session.started_at < hour_end
            )
            
            usage_data.append({
                'Hour': hour_start.strftime('%H:%M'),
                'Tokens': hour_tokens,
                'Cost': hour_cost
            })
        
        return pd.DataFrame(usage_data)
        
    except Exception as e:
        # Return empty DataFrame on error
        return pd.DataFrame(columns=['Hour', 'Tokens', 'Cost'])
    finally:
        if db:
            db.close()


def display_usage_graphs():
    """
    Display usage graphs showing token and cost trends over time.
    """
    st.subheader("📈 Usage Trends (Last 24 Hours)")
    
    usage_df = fetch_usage_timeline()
    
    if usage_df.empty:
        show_info_message("No usage data available for the last 24 hours.")
        return
    
    # Create two columns for side-by-side charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Token Usage by Hour**")
        if usage_df['Tokens'].sum() > 0:
            st.line_chart(usage_df.set_index('Hour')['Tokens'])
        else:
            st.info("No token usage in the last 24 hours")
    
    with col2:
        st.write("**Cost by Hour**")
        if usage_df['Cost'].sum() > 0:
            st.line_chart(usage_df.set_index('Hour')['Cost'])
        else:
            st.info("No costs in the last 24 hours")
    
    # Summary stats
    total_tokens = usage_df['Tokens'].sum()
    total_cost = usage_df['Cost'].sum()
    peak_hour_tokens = usage_df['Tokens'].max()
    peak_hour_cost = usage_df['Cost'].max()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("24h Tokens", format_tokens(total_tokens))
    with col2:
        st.metric("24h Cost", format_cost(total_cost))
    with col3:
        st.metric("Peak Hour Tokens", format_tokens(peak_hour_tokens))
    with col4:
        st.metric("Peak Hour Cost", format_cost(peak_hour_cost))


def display_service_health():
    """
    Display service health status including API and database.
    """
    st.subheader("💚 Service Health Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Anthropic API Service**")
        try:
            anthropic_service = get_anthropic_service()
            status_info = anthropic_service.get_service_status()
            
            # Map status to emoji and color
            status_emoji = {
                'healthy': '🟢',
                'degraded': '🟡', 
                'unavailable': '🔴'
            }
            
            status = status_info.get('status', 'unknown')
            st.write(f"{status_emoji.get(status, '⚪')} **Status:** {status.title()}")
            st.write(f"**Model:** {status_info.get('model', 'Unknown')}")
            st.write(f"**Environment:** {status_info.get('environment', 'Unknown')}")
            st.write(f"**Circuit Breaker:** {status_info.get('circuit_breaker_state', 'Unknown')}")
            
            # Cost information
            daily_cost = status_info.get('daily_cost', 0.0)
            daily_limit = status_info.get('daily_limit', 10.0)
            cost_percentage = (daily_cost / daily_limit) * 100 if daily_limit > 0 else 0
            
            st.write(f"**Daily Cost:** {format_cost(daily_cost)} / {format_cost(daily_limit)} ({cost_percentage:.1f}%)")
            
            # Show last error if any
            last_error = status_info.get('last_error')
            if last_error:
                with st.expander("⚠️ Last Error Details"):
                    st.code(f"Type: {last_error.get('type', 'Unknown')}\nMessage: {last_error.get('message', 'No details')}\nTime: {last_error.get('timestamp', 'Unknown')}")
        except Exception as e:
            st.write(f"🔴 **Status:** Unavailable")
            st.write(f"**Error:** {str(e)}")
    
    with col2:
        st.write("**Database Service**")
        try:
            db = get_database_connection()
            # Simple test query
            test_count = session_service.count(db=db)
            db.close()
            
            st.write(f"🟢 **Status:** Healthy")
            st.write(f"**Connection:** Active")
            st.write(f"**Total Sessions:** {test_count}")
            st.write(f"**Last Check:** {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            st.write(f"🔴 **Status:** Unavailable")
            st.write(f"**Error:** {str(e)}")


def display_error_logs():
    """
    Display recent error logs and system issues.
    """
    st.subheader("📋 Recent Issues")
    
    # For MVP, show simple error tracking
    # In production, this would read from actual log files
    
    errors = []
    
    # Check Anthropic service errors
    try:
        anthropic_service = get_anthropic_service()
        status_info = anthropic_service.get_service_status()
        last_error = status_info.get('last_error')
        if last_error:
            errors.append({
                'timestamp': last_error.get('timestamp', 'Unknown'),
                'service': 'Anthropic API',
                'type': last_error.get('type', 'Unknown'),
                'message': last_error.get('message', 'No details'),
                'severity': 'High' if last_error.get('type') in ['authentication', 'connection'] else 'Medium'
            })
    except Exception as e:
        errors.append({
            'timestamp': datetime.now().isoformat(),
            'service': 'Anthropic API',
            'type': 'service_error',
            'message': str(e),
            'severity': 'High'
        })
    
    # Check database errors (simple check)
    try:
        db = get_database_connection()
        db.close()
    except Exception as e:
        errors.append({
            'timestamp': datetime.now().isoformat(),
            'service': 'Database',
            'type': 'connection_error',
            'message': str(e),
            'severity': 'Critical'
        })
    
    if not errors:
        st.success("✅ No recent errors detected!")
        st.info("System appears to be running smoothly.")
    else:
        st.warning(f"⚠️ Found {len(errors)} recent issue(s):")
        
        for error in errors:
            severity_color = {
                'Critical': '🔴',
                'High': '🟠', 
                'Medium': '🟡',
                'Low': '🟢'
            }
            
            with st.expander(f"{severity_color.get(error['severity'], '⚪')} {error['service']} - {error['type']}"):
                st.write(f"**Timestamp:** {error['timestamp']}")
                st.write(f"**Severity:** {error['severity']}")
                st.write(f"**Service:** {error['service']}")
                st.write(f"**Type:** {error['type']}")
                st.write(f"**Message:** {error['message']}")


def handle_auto_refresh():
    """
    Handle auto-refresh functionality with session state management.
    """
    # Initialize auto-refresh state if not exists
    if 'auto_refresh_enabled' not in st.session_state:
        st.session_state.auto_refresh_enabled = False
    if 'last_refresh_time' not in st.session_state:
        st.session_state.last_refresh_time = time.time()
    
    # Auto-refresh logic
    if st.session_state.auto_refresh_enabled:
        current_time = time.time()
        # Refresh every 30 seconds
        if current_time - st.session_state.last_refresh_time >= 30:
            st.session_state.last_refresh_time = current_time
            st.rerun()


def main():
    # Configure page
    setup_page_config(
        page_title="Admin Monitor - Virtual Client",
        page_icon="📊"
    )
    
    # Initialize session state
    initialize_session_state()
    
    st.title("📊 Admin Monitoring Dashboard")
    st.markdown("Monitor system usage and active sessions in real-time")
    
    # Refresh button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Refresh Data", type="primary"):
            st.rerun()
    
    with col2:
        # Auto-refresh toggle (now enabled!)
        auto_refresh = st.checkbox(
            "Auto-refresh (30s)", 
            value=st.session_state.get('auto_refresh_enabled', False),
            help="Automatically refresh dashboard every 30 seconds"
        )
        st.session_state.auto_refresh_enabled = auto_refresh
    
    # Handle auto-refresh
    handle_auto_refresh()
    
    st.divider()
    
    # Main metrics display
    display_admin_metrics()
    
    st.divider()
    
    # Usage graphs
    display_usage_graphs()
    
    st.divider()
    
    # Service health status
    display_service_health()
    
    st.divider()
    
    # Session overview
    display_session_overview()
    
    st.divider()
    
    # Error logs
    display_error_logs()
    
    # Footer info
    st.markdown("---")
    st.caption(
        "💡 **Admin Tips:** Use this dashboard to monitor system usage, service health, and identify issues. "
        "Auto-refresh keeps data current. For detailed analysis, consider exporting data from the database directly."
    )


if __name__ == "__main__":
    main()
