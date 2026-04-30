from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["privacy"])

@router.get("/privacy-policy", response_class=HTMLResponse)
def get_privacy_policy():
    """Serve the privacy policy page"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - Eagle's Pride</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
        }
        .last-updated {
            color: #7f8c8d;
            font-style: italic;
        }
        .contact {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <h1>Privacy Policy for Eagle's Pride</h1>
    <p class="last-updated">Last updated: April 30, 2026</p>

    <h2>1. Introduction</h2>
    <p>Eagle's Pride ("we", "our", "us") operates a job seeking and recruitment mobile application. We respect your privacy and are committed to protecting your personal data. This privacy policy explains how we collect, use, and safeguard your information when you use our app.</p>

    <h2>2. Information We Collect</h2>
    <p>We collect the following types of information:</p>
    <ul>
        <li><strong>Personal Information:</strong> Name, email address, phone number, location</li>
        <li><strong>Profile Data:</strong> Resume, work experience, education, skills, and qualifications</li>
        <li><strong>Job Application Data:</strong> Applications submitted, job preferences, saved jobs</li>
        <li><strong>Camera Images:</strong> Profile photos and document uploads (resume, certificates, ID verification)</li>
        <li><strong>Communication Data:</strong> Messages between job seekers and employers</li>
        <li><strong>Payment Information:</strong> Subscription and payment transaction details (processed securely through third-party payment providers)</li>
        <li><strong>Usage Data:</strong> App usage statistics, device information, and analytics</li>
    </ul>

    <h2>3. How We Use Your Information</h2>
    <p>We use your information for the following purposes:</p>
    <ul>
        <li>To provide job matching and recruitment services</li>
        <li>To facilitate communication between job seekers and employers</li>
        <li>To process job applications and manage subscriptions</li>
        <li>To verify user identity and credentials</li>
        <li>To send notifications about job opportunities and application updates</li>
        <li>To improve our services and user experience</li>
        <li>To comply with legal obligations</li>
    </ul>

    <h2>4. Camera Permission</h2>
    <p>We request camera access for the following purposes:</p>
    <ul>
        <li>Taking profile photos</li>
        <li>Uploading documents for verification (resume, certificates, ID)</li>
        <li>Scanning QR codes for quick actions</li>
    </ul>
    <p>Camera images are only used for the purposes stated above and are stored securely. You can choose to upload images from your gallery instead of using the camera.</p>

    <h2>5. Data Storage and Security</h2>
    <p>We implement industry-standard security measures to protect your data:</p>
    <ul>
        <li>Data is stored on secure, encrypted servers</li>
        <li>We use HTTPS encryption for data transmission</li>
        <li>Access to personal data is restricted to authorized personnel only</li>
        <li>Regular security audits and updates are performed</li>
    </ul>

    <h2>6. Data Sharing</h2>
    <p>We share your information in the following circumstances:</p>
    <ul>
        <li><strong>With Employers:</strong> When you apply for a job, your profile and application are shared with the employer</li>
        <li><strong>With Service Providers:</strong> We use third-party services for payment processing, email delivery, and analytics</li>
        <li><strong>Legal Requirements:</strong> We may disclose information if required by law or to protect our rights</li>
    </ul>
    <p><strong>We do not sell your personal data to third parties.</strong></p>

    <h2>7. Your Rights</h2>
    <p>You have the following rights regarding your personal data:</p>
    <ul>
        <li><strong>Access:</strong> Request a copy of your personal data</li>
        <li><strong>Correction:</strong> Update or correct your information</li>
        <li><strong>Deletion:</strong> Request deletion of your account and data</li>
        <li><strong>Opt-out:</strong> Unsubscribe from marketing communications</li>
        <li><strong>Data Portability:</strong> Request your data in a portable format</li>
    </ul>

    <h2>8. Data Retention</h2>
    <p>We retain your personal data for as long as your account is active or as needed to provide services. If you delete your account, we will delete your personal data within 30 days, except where we are required to retain it for legal purposes.</p>

    <h2>9. Children's Privacy</h2>
    <p>Our app is not intended for users under the age of 16. We do not knowingly collect personal information from children. If you believe we have collected information from a child, please contact us immediately.</p>

    <h2>10. Third-Party Services</h2>
    <p>Our app uses the following third-party services:</p>
    <ul>
        <li>Payment processors for subscription payments</li>
        <li>Email service providers for notifications</li>
        <li>Analytics services to improve app performance</li>
    </ul>
    <p>These services have their own privacy policies, and we encourage you to review them.</p>

    <h2>11. Changes to This Privacy Policy</h2>
    <p>We may update this privacy policy from time to time. We will notify you of any significant changes by posting the new policy in the app and updating the "Last updated" date. Your continued use of the app after changes constitutes acceptance of the updated policy.</p>

    <h2>12. International Data Transfers</h2>
    <p>Your data may be transferred to and processed in countries other than your own. We ensure appropriate safeguards are in place to protect your data in accordance with this privacy policy.</p>

    <div class="contact">
        <h2>13. Contact Us</h2>
        <p>If you have any questions about this privacy policy or wish to exercise your rights, please contact us:</p>
        <p>
            <strong>Email:</strong> support@eaglespride.com<br>
            <strong>App:</strong> Eagle's Pride<br>
            <strong>Developer:</strong> BugBuild
        </p>
    </div>
</body>
</html>
    """
    return html_content
