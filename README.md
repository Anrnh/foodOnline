---

# 🎓 UNIMAS Student Pavilion Cafeteria Management System

Welcome to the **UNIMAS Student Pavilion Cafeteria Management System** project! This system is designed to revolutionize the way students and staff interact with the university's cafeteria services. By bringing modern technology to the heart of campus dining, this platform aims to streamline operations, reduce wait times, and enhance the overall experience for everyone involved.

## 🚀 Purpose

The UNIMAS Student Pavilion Cafeteria Management System is built to tackle the common challenges faced in a university cafeteria environment:

- **Long Queues**: Tired of waiting in line? Our system allows students and staff to place orders online, so your food is ready when you are.
- **Manual Processes**: Say goodbye to outdated, error-prone manual ordering systems. Our web-based platform ensures accuracy and efficiency in every order.
- **Payment Hassles**: We've integrated digital payment options to make transactions quick, easy, and secure.
  
This project is not just a solution; it’s a step towards a more connected and efficient campus life.

## 🛠 Installation Instructions

Setting up the UNIMAS Student Pavilion Cafeteria Management System is straightforward. Here’s how you can get started:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Anrnh/foodOnline.git
   cd foodOnline
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows, use `env\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```
   Open your web browser and navigate to `http://localhost:8000` to start using the system.

6. **Create an Admin User**:
   ```bash
   python manage.py createsuperuser
   ```
   Set up your credentials, and you’re ready to manage the system.

## 🎯 Usage

### For Students:
- **Sign Up**: Register with your student credentials.
- **Browse & Order**: Explore available cafeterias and menus, and place your order online.
- **Get Notified**: Receive an email notification once your order is placed successfully.
- **Pick Up**: Skip the line and pick up your food at the cafeteria.

### For Cafeteria Vendors:
- **Manage Your Dashboard**: Log in to manage your menu, schedule, and handle orders efficiently.
- **Track Orders**: Stay on top of transactions and customer preferences with real-time data.

### For Administrators:
- **Oversee Operations**: Manage users, monitor orders, and keep the system running smoothly.

## 🌟 Features

- **Seamless Digital Ordering**: Easily browse, select, and order meals online.
- **Vendor & Admin Dashboards**: Intuitive interfaces for vendors to manage operations and for administrators to oversee the system.
- **Email Notifications**: Automatic confirmation emails are sent after successful orders.
- **Secure Payments**: Integrated payment options for fast and secure transactions.
- **Responsive Design**: Access the system across various devices, making it convenient whether you’re on a laptop, tablet, or phone.

## 🤝 Contributing

We believe in the power of collaboration. Contributions are more than welcome! If you’re interested in improving the system, here’s how you can help:

1. **Fork the Repo**: Create your own fork of the repository.
2. **Create a Branch**: Work on your changes in a feature branch.
3. **Submit a PR**: Open a pull request with a clear description of what you’ve done.
4. **Review & Merge**: After approval, your changes will be merged into the main branch.

## 📄 License

Feel free to use, modify, and distribute.

## 🙏 Acknowledgments

A special thanks to the UNIMAS community for their continuous feedback and support. This project wouldn’t have been possible without the collaboration of students, staff, and cafeteria vendors.

## ❓ FAQs

**Q: Can I access this system on my mobile device?**  
A: Yes! While the current system is optimized for web browsers, it is fully responsive and accessible via mobile devices.

**Q: How do I report an issue or request a new feature?**  
A: Please open an issue in the GitHub repository, and we’ll address it as soon as possible.

## 🔧 Troubleshooting

- **Server Not Starting**: Ensure all dependencies are installed and the virtual environment is activated.
- **Database Errors**: If you encounter migration issues, try `python manage.py migrate --fake` to resolve conflicts.

---
