from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func

from models import db, ConversationMetrics, DailyMetrics, User, Organization
from utils.permissions import has_organization_access

analytics_routes = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_routes.route('/overview', methods=['GET'])
@jwt_required()
def get_analytics_overview():
    """Get overview analytics for an organization"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get organization_id from query params or use user's organization
    organization_id = request.args.get('organization_id', type=int) or user.organization_id
    
    # Check permissions
    if not has_organization_access(organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get date range (default to last 30 days)
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=30)
    
    if request.args.get('start_date'):
        try:
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid start_date format (use YYYY-MM-DD)'}), 400
    
    if request.args.get('end_date'):
        try:
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid end_date format (use YYYY-MM-DD)'}), 400
    
    # Get metrics
    metrics = ConversationMetrics.query.filter(
        ConversationMetrics.organization_id == organization_id,
        ConversationMetrics.created_at >= start_date,
        ConversationMetrics.created_at <= end_date + timedelta(days=1)
    ).all()
    
    # Calculate overview stats
    total_conversations = len(metrics)
    total_messages = sum(m.message_count for m in metrics)
    lead_count = sum(1 for m in metrics if m.lead_captured)
    completion_rate = sum(1 for m in metrics if m.completed) / total_conversations if total_conversations > 0 else 0
    
    avg_duration = 0
    if total_conversations > 0:
        durations = [m.duration_seconds for m in metrics if m.duration_seconds is not None]
        avg_duration = sum(durations) / len(durations) if durations else 0
    
    # Time of day breakdown
    time_breakdown = {
        'business': sum(1 for m in metrics if m.time_of_day == 'business'),
        'evening': sum(1 for m in metrics if m.time_of_day == 'evening'),
        'night': sum(1 for m in metrics if m.time_of_day == 'night'),
        'weekend': sum(1 for m in metrics if m.time_of_day == 'weekend')
    }
    
    # Source breakdown
    source_breakdown = {}
    for metric in metrics:
        if metric.utm_source:
            source_breakdown[metric.utm_source] = source_breakdown.get(metric.utm_source, 0) + 1
    
    # Prepare data for daily trend chart
    daily_trends = db.session.query(
        func.date(ConversationMetrics.created_at).label('date'),
        func.count().label('count')
    ).filter(
        ConversationMetrics.organization_id == organization_id,
        ConversationMetrics.created_at >= start_date,
        ConversationMetrics.created_at <= end_date + timedelta(days=1)
    ).group_by(
        func.date(ConversationMetrics.created_at)
    ).all()
    
    # Format for response
    daily_data = []
    current_date = start_date
    while current_date <= end_date:
        day_data = next((d for d in daily_trends if d.date == current_date), None)
        daily_data.append({
            'date': current_date.isoformat(),
            'conversations': day_data.count if day_data else 0
        })
        current_date += timedelta(days=1)
    
    return jsonify({
        'total_conversations': total_conversations,
        'total_messages': total_messages,
        'lead_count': lead_count,
        'lead_conversion_rate': lead_count / total_conversations if total_conversations > 0 else 0,
        'avg_conversation_duration': avg_duration,
        'completion_rate': completion_rate,
        'time_breakdown': time_breakdown,
        'source_breakdown': source_breakdown,
        'daily_trend': daily_data
    }), 200

@analytics_routes.route('/leads', methods=['GET'])
@jwt_required()
def get_lead_analytics():
    """Get lead analytics"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get organization_id from query params or use user's organization
    organization_id = request.args.get('organization_id', type=int) or user.organization_id
    
    # Check permissions
    if not has_organization_access(organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get date range (default to last 30 days)
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=30)
    
    if request.args.get('start_date'):
        try:
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid start_date format (use YYYY-MM-DD)'}), 400
    
    if request.args.get('end_date'):
        try:
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid end_date format (use YYYY-MM-DD)'}), 400
    
    # Get lead metrics
    metrics = ConversationMetrics.query.filter(
        ConversationMetrics.organization_id == organization_id,
        ConversationMetrics.created_at >= start_date,
        ConversationMetrics.created_at <= end_date + timedelta(days=1),
        ConversationMetrics.lead_captured == True
    ).all()
    
    # Calculate lead stats
    total_leads = len(metrics)
    
    # Source breakdown
    source_breakdown = {}
    for metric in metrics:
        if metric.utm_source:
            source_breakdown[metric.utm_source] = source_breakdown.get(metric.utm_source, 0) + 1
    
    # Daily lead trend
    daily_leads = db.session.query(
        func.date(ConversationMetrics.created_at).label('date'),
        func.count().label('count')
    ).filter(
        ConversationMetrics.organization_id == organization_id,
        ConversationMetrics.created_at >= start_date,
        ConversationMetrics.created_at <= end_date + timedelta(days=1),
        ConversationMetrics.lead_captured == True
    ).group_by(
        func.date(ConversationMetrics.created_at)
    ).all()
    
    # Format for response
    daily_data = []
    current_date = start_date
    while current_date <= end_date:
        day_data = next((d for d in daily_leads if d.date == current_date), None)
        daily_data.append({
            'date': current_date.isoformat(),
            'leads': day_data.count if day_data else 0
        })
        current_date += timedelta(days=1)
    
    return jsonify({
        'total_leads': total_leads,
        'source_breakdown': source_breakdown,
        'daily_trend': daily_data
    }), 200

@analytics_routes.route('/sources', methods=['GET'])
@jwt_required()
def get_source_analytics():
    """Get traffic source analytics"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get organization_id from query params or use user's organization
    organization_id = request.args.get('organization_id', type=int) or user.organization_id
    
    # Check permissions
    if not has_organization_access(organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get date range (default to last 30 days)
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=30)
    
    if request.args.get('start_date'):
        try:
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid start_date format (use YYYY-MM-DD)'}), 400
    
    if request.args.get('end_date'):
        try:
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid end_date format (use YYYY-MM-DD)'}), 400
    
    # Get metrics
    metrics = ConversationMetrics.query.filter(
        ConversationMetrics.organization_id == organization_id,
        ConversationMetrics.created_at >= start_date,
        ConversationMetrics.created_at <= end_date + timedelta(days=1)
    ).all()
    
    # Source breakdown
    sources = {}
    for metric in metrics:
        source = metric.utm_source or 'direct'
        if source not in sources:
            sources[source] = {
                'conversations': 0,
                'leads': 0,
                'completed': 0
            }
        
        sources[source]['conversations'] += 1
        if metric.lead_captured:
            sources[source]['leads'] += 1
        if metric.completed:
            sources[source]['completed'] += 1
    
    # Calculate conversion rates
    for source in sources:
        total = sources[source]['conversations']
        sources[source]['lead_rate'] = sources[source]['leads'] / total if total > 0 else 0
        sources[source]['completion_rate'] = sources[source]['completed'] / total if total > 0 else 0
    
    # Format for response
    source_data = [
        {
            'source': source,
            'conversations': data['conversations'],
            'leads': data['leads'],
            'lead_rate': data['lead_rate'],
            'completion_rate': data['completion_rate']
        }
        for source, data in sources.items()
    ]
    
    # Sort by conversation count descending
    source_data.sort(key=lambda x: x['conversations'], reverse=True)
    
    return jsonify({
        'sources': source_data
    }), 200

@analytics_routes.route('/time', methods=['GET'])
@jwt_required()
def get_time_analytics():
    """Get time-based analytics"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get organization_id from query params or use user's organization
    organization_id = request.args.get('organization_id', type=int) or user.organization_id
    
    # Check permissions
    if not has_organization_access(organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get date range (default to last 30 days)
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=30)
    
    if request.args.get('start_date'):
        try:
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid start_date format (use YYYY-MM-DD)'}), 400
    
    if request.args.get('end_date'):
        try:
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid end_date format (use YYYY-MM-DD)'}), 400
    
    # Get metrics
    metrics = ConversationMetrics.query.filter(
        ConversationMetrics.organization_id == organization_id,
        ConversationMetrics.created_at >= start_date,
        ConversationMetrics.created_at <= end_date + timedelta(days=1)
    ).all()
    
    # Time of day breakdown
    time_periods = {
        'business': {'conversations': 0, 'leads': 0},
        'evening': {'conversations': 0, 'leads': 0},
        'night': {'conversations': 0, 'leads': 0},
        'weekend': {'conversations': 0, 'leads': 0}
    }
    
    for metric in metrics:
        period = metric.time_of_day
        if period in time_periods:
            time_periods[period]['conversations'] += 1
            if metric.lead_captured:
                time_periods[period]['leads'] += 1
    
    # Hour of day analysis
    hour_data = {}
    for metric in metrics:
        hour = metric.hour_of_day
        if hour not in hour_data:
            hour_data[hour] = {'conversations': 0, 'leads': 0}
        
        hour_data[hour]['conversations'] += 1
        if metric.lead_captured:
            hour_data[hour]['leads'] += 1
    
    # Format hour data for response
    hourly_trend = []
    for hour in range(24):
        data = hour_data.get(hour, {'conversations': 0, 'leads': 0})
        hourly_trend.append({
            'hour': hour,
            'conversations': data['conversations'],
            'leads': data['leads']
        })
    
    return jsonify({
        'time_periods': [
            {
                'period': period,
                'conversations': data['conversations'],
                'leads': data['leads'],
                'lead_rate': data['leads'] / data['conversations'] if data['conversations'] > 0 else 0
            }
            for period, data in time_periods.items()
        ],
        'hourly_trend': hourly_trend
    }), 200

@analytics_routes.route('/efficiency', methods=['GET'])
@jwt_required()
def get_efficiency_analytics():
    """Get efficiency and cost savings estimates"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get organization_id from query params or use user's organization
    organization_id = request.args.get('organization_id', type=int) or user.organization_id
    
    # Check permissions
    if not has_organization_access(organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get date range (default to last 30 days)
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=30)
    
    if request.args.get('start_date'):
        try:
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid start_date format (use YYYY-MM-DD)'}), 400
    if request.args.get('end_date'):
        try:
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid end_date format (use YYYY-MM-DD)'}), 400
    
    # Get metrics
    metrics = ConversationMetrics.query.filter(
        ConversationMetrics.organization_id == organization_id,
        ConversationMetrics.created_at >= start_date,
        ConversationMetrics.created_at <= end_date + timedelta(days=1)
    ).all()
    
    # Calculate efficiency stats
    total_conversations = len(metrics)
    total_messages = sum(m.message_count for m in metrics)
    
    # Estimate time saved based on average handling times
    avg_human_handling_time = 180  # seconds per conversation (3 minutes)
    avg_bot_handling_time = 60  # seconds of human oversight needed per bot conversation
    
    time_saved_seconds = total_conversations * (avg_human_handling_time - avg_bot_handling_time)
    time_saved_hours = time_saved_seconds / 3600
    
    # Estimate cost savings based on hourly rate
    hourly_rate = request.args.get('hourly_rate', 25, type=float)  # Default $25/hour
    cost_savings = time_saved_hours * hourly_rate
    
    # Calculate savings by time period
    time_period_savings = {}
    for period in ['business', 'evening', 'night', 'weekend']:
        period_count = sum(1 for m in metrics if m.time_of_day == period)
        period_time_saved = period_count * (avg_human_handling_time - avg_bot_handling_time) / 3600
        time_period_savings[period] = {
            'conversations': period_count,
            'hours_saved': period_time_saved,
            'cost_savings': period_time_saved * hourly_rate
        }
    
    return jsonify({
        'total_conversations': total_conversations,
        'total_messages': total_messages,
        'time_saved_hours': time_saved_hours,
        'cost_savings': cost_savings,
        'hourly_rate_used': hourly_rate,
        'time_period_breakdown': time_period_savings,
        'equivalent_full_time': time_saved_hours / (40 * 4)  # Assuming 40-hour work week, 4 weeks per month
    }), 200
            

