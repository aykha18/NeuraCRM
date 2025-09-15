import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, Eye, EyeOff, Building2, User, Mail, Lock, Globe, CreditCard } from 'lucide-react';
import { organizationService } from '../services/organization';
import type { SubscriptionPlan, OrganizationSignupRequest } from '../services/organization';

const OrganizationSignup: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<string>('free');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const [formData, setFormData] = useState<OrganizationSignupRequest>({
    organization_name: '',
    organization_domain: '',
    admin_name: '',
    admin_email: '',
    admin_password: '',
    plan: 'free'
  });

  useEffect(() => {
    loadSubscriptionPlans();
  }, []);

  const loadSubscriptionPlans = async () => {
    try {
      const plansData = await organizationService.getSubscriptionPlans();
      setPlans(plansData);
    } catch (error) {
      console.error('Failed to load subscription plans:', error);
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.organization_name.trim()) {
      newErrors.organization_name = 'Organization name is required';
    } else if (formData.organization_name.trim().length < 2) {
      newErrors.organization_name = 'Organization name must be at least 2 characters';
    }

    if (!formData.admin_name.trim()) {
      newErrors.admin_name = 'Admin name is required';
    } else if (formData.admin_name.trim().length < 2) {
      newErrors.admin_name = 'Admin name must be at least 2 characters';
    }

    if (!formData.admin_email.trim()) {
      newErrors.admin_email = 'Admin email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.admin_email)) {
      newErrors.admin_email = 'Please enter a valid email address';
    }

    if (!formData.admin_password) {
      newErrors.admin_password = 'Password is required';
    } else if (formData.admin_password.length < 8) {
      newErrors.admin_password = 'Password must be at least 8 characters';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.admin_password)) {
      newErrors.admin_password = 'Password must contain at least one uppercase letter, one lowercase letter, and one number';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      const signupData = {
        ...formData,
        plan: selectedPlan
      };

      const response = await organizationService.signupOrganization(signupData);
      
      // Store the access token
      localStorage.setItem('access_token', response.access_token);
      
      // Redirect to dashboard
      navigate('/dashboard');
    } catch (error: any) {
      console.error('Organization signup failed:', error);
      setErrors({ 
        general: error.message || 'Failed to create organization. Please try again.' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: keyof OrganizationSignupRequest, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined as any }));
    }
  };

  const renderStep1 = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Choose Your Plan</h2>
        <p className="text-gray-600">Select the perfect plan for your organization</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`relative p-6 rounded-xl border-2 cursor-pointer transition-all ${
              selectedPlan === plan.name
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => setSelectedPlan(plan.name)}
          >
            {selectedPlan === plan.name && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <div className="bg-blue-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                  Selected
                </div>
              </div>
            )}
            
            <div className="text-center">
              <h3 className="text-xl font-bold text-gray-900 mb-2">{plan.display_name}</h3>
              <div className="mb-4">
                <span className="text-3xl font-bold text-gray-900">${plan.price_monthly}</span>
                <span className="text-gray-600">/month</span>
              </div>
              <p className="text-gray-600 text-sm mb-4">{plan.description}</p>
              
              <div className="space-y-2 text-sm">
                {plan.features.map((feature, index) => (
                  <div key={index} className="flex items-center text-gray-700">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                    {feature}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="flex justify-center">
        <button
          type="button"
          onClick={() => setCurrentStep(2)}
          className="bg-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Continue to Organization Details
        </button>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Organization Details</h2>
        <p className="text-gray-600">Tell us about your organization</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Building2 className="w-4 h-4 inline mr-2" />
              Organization Name *
            </label>
            <input
              type="text"
              value={formData.organization_name}
              onChange={(e) => handleInputChange('organization_name', e.target.value)}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.organization_name ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Your Company Name"
            />
            {errors.organization_name && (
              <p className="text-red-500 text-sm mt-1">{errors.organization_name}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Globe className="w-4 h-4 inline mr-2" />
              Organization Domain (Optional)
            </label>
            <input
              type="text"
              value={formData.organization_domain}
              onChange={(e) => handleInputChange('organization_domain', e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="yourcompany.com"
            />
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <User className="w-4 h-4 inline mr-2" />
              Admin Name *
            </label>
            <input
              type="text"
              value={formData.admin_name}
              onChange={(e) => handleInputChange('admin_name', e.target.value)}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.admin_name ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Your Full Name"
            />
            {errors.admin_name && (
              <p className="text-red-500 text-sm mt-1">{errors.admin_name}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Mail className="w-4 h-4 inline mr-2" />
              Admin Email *
            </label>
            <input
              type="email"
              value={formData.admin_email}
              onChange={(e) => handleInputChange('admin_email', e.target.value)}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.admin_email ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="admin@yourcompany.com"
            />
            {errors.admin_email && (
              <p className="text-red-500 text-sm mt-1">{errors.admin_email}</p>
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Lock className="w-4 h-4 inline mr-2" />
            Admin Password *
          </label>
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              value={formData.admin_password}
              onChange={(e) => handleInputChange('admin_password', e.target.value)}
              className={`w-full px-4 py-3 pr-12 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.admin_password ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Create a strong password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
            >
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          {errors.admin_password && (
            <p className="text-red-500 text-sm mt-1">{errors.admin_password}</p>
          )}
        </div>

        {errors.general && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-600 text-sm">{errors.general}</p>
          </div>
        )}

        <div className="flex justify-between">
          <button
            type="button"
            onClick={() => setCurrentStep(1)}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
          >
            Back to Plans
          </button>
          
          <button
            type="submit"
            disabled={isLoading}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Creating Organization...
              </>
            ) : (
              <>
                <CreditCard className="w-4 h-4 mr-2" />
                Create Organization
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Start Your CRM Journey
            </h1>
            <p className="text-xl text-gray-600">
              Create your organization and get started with NeuraCRM in minutes
            </p>
          </div>

          {/* Progress Steps */}
          <div className="flex justify-center mb-8">
            <div className="flex items-center space-x-4">
              <div className={`flex items-center ${currentStep >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  currentStep >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-400'
                }`}>
                  1
                </div>
                <span className="ml-2 font-medium">Choose Plan</span>
              </div>
              <div className="w-8 h-0.5 bg-gray-300"></div>
              <div className={`flex items-center ${currentStep >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  currentStep >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-400'
                }`}>
                  2
                </div>
                <span className="ml-2 font-medium">Organization Details</span>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            {currentStep === 1 && renderStep1()}
            {currentStep === 2 && renderStep2()}
          </div>

          {/* Footer */}
          <div className="text-center mt-8">
            <p className="text-gray-600">
              Already have an account?{' '}
              <button
                onClick={() => navigate('/signin')}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Sign in here
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrganizationSignup;
