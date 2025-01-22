import os, random
from django.shortcuts import render, redirect
from .models import HarassmentReport
from .forms import HarassmentReportForm
from geopy.geocoders import Nominatim

def home(request):
    # Get all reports from the database
    reports = HarassmentReport.objects.all()
    
    # Convert reports to a format suitable for JavaScript
    reports_data = [
        {
            'lat': report.latitude,  # Make sure these match your model field names
            'lng': report.longitude,
            'location': report.location,
            'type': report.harassment_type
        } for report in reports
    ]
    
    # Import json
    import json
    
    context = {
        'reports': json.dumps(reports_data)
    }
    
    return render(request, 'home.html', context)


def reports_list(request):
    reports = HarassmentReport.objects.all().order_by('-timestamp')

    # Apply filters
    type_filter = request.GET.get('type')
    location_filter = request.GET.get('location')
    if type_filter:
        reports = reports.filter(harassment_type=type_filter)
    if location_filter:
        reports = reports.filter(location__icontains=location_filter)

    # Assign random profile images
    images = os.listdir('harassment_platform/static/images/profile_pictures/')
    for report in reports:
        report.random_image = random.choice(images)

    return render(request, 'reports.html', {'reports': reports})

def report_submission(request):
    if request.method == "POST":
        location = request.POST.get('location')
        date = request.POST.get('date')
        time = request.POST.get('time')
        harassment_type = request.POST.get('harassment_type')
        reported_by = request.POST.get('reported_by')
        description = request.POST.get('description')
        

        # Validate harassment_type
        if not harassment_type:
            return render(request, 'report_submission.html', {'error': 'Harassment type is required.'})

        try:
            # Geocode the location to get latitude and longitude
            geolocator = Nominatim(user_agent="harassment_report_app")
            location_data = geolocator.geocode(location)
            
            if location_data:
                latitude = location_data.latitude
                longitude = location_data.longitude
            else:
                return render(request, 'report_submission.html', 
                            {'error': 'Could not find coordinates for the given location.'})

            # Save the data to the database
            HarassmentReport.objects.create(
                location=location,
                date=date,
                time=time,
                harassment_type=harassment_type,
                description=description,
                latitude=latitude,
                longitude=longitude
            )

            # Add a success message and redirect to the same page
            return render(request, 'report_submission.html', {'success': True})
            
        except Exception as e:
            return render(request, 'report_submission.html', 
                        {'error': f'Error processing location: {str(e)}'})
    
    return render(request, 'report_submission.html')
