import React from 'react';
import { motion } from 'framer-motion';
import { FormField } from '../types';

interface AppointmentFormProps {
  fields: FormField[];
  onSubmit: (data: Record<string, string>) => void;
  onChange?: (data: Record<string, string>) => void;
  isLoading?: boolean;
  submitLabel?: string;
  className?: string;
}

const AppointmentForm: React.FC<AppointmentFormProps> = ({
  fields,
  onSubmit,
  onChange,
  isLoading = false,
  submitLabel = 'Submit',
  className = ''
}) => {
  const [formData, setFormData] = React.useState<Record<string, string>>({});
  const [errors, setErrors] = React.useState<Record<string, string>>({});

  const handleInputChange = (name: string, value: string) => {
    const newData = { ...formData, [name]: value };
    setFormData(newData);
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
    // Call onChange callback if provided
    if (onChange) {
      onChange(newData);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    fields.forEach(field => {
      if (field.required && !formData[field.name]?.trim()) {
        newErrors[field.name] = `${field.label} is required`;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const getFieldIcon = (fieldName: string) => {
    const iconMap: Record<string, string> = {
      id_number: '👤',
      doctor_name: '🩺',
      specialisation: '🩺',
      date: '📅',
      time: '🕐',
      old_date: '📅',
      new_date: '📅',
      query: '📝',
    };
    return iconMap[fieldName] || '📝';
  };

  const renderField = (field: FormField) => {
    const commonClasses = `w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${
      errors[field.name] ? 'border-red-300 bg-red-50' : 'border-gray-300 bg-white'
    }`;

    switch (field.type) {
      case 'select':
        return (
          <select
            name={field.name}
            value={formData[field.name] || ''}
            onChange={(e) => handleInputChange(field.name, e.target.value)}
            className={commonClasses}
            required={field.required}
          >
            <option value="">Select {field.label}</option>
            {field.options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'textarea':
        return (
          <textarea
            name={field.name}
            value={formData[field.name] || ''}
            onChange={(e) => handleInputChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            className={`${commonClasses} resize-none`}
            rows={4}
            required={field.required}
          />
        );

      case 'date':
        return (
          <input
            type="date"
            name={field.name}
            value={formData[field.name] || ''}
            onChange={(e) => handleInputChange(field.name, e.target.value)}
            className={commonClasses}
            required={field.required}
            min={new Date().toISOString().split('T')[0]}
          />
        );

      case 'time':
        return (
          <input
            type="time"
            name={field.name}
            value={formData[field.name] || ''}
            onChange={(e) => handleInputChange(field.name, e.target.value)}
            className={commonClasses}
            required={field.required}
          />
        );

      case 'number':
        return (
          <input
            type="number"
            name={field.name}
            value={formData[field.name] || ''}
            onChange={(e) => handleInputChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            className={commonClasses}
            required={field.required}
            min={1000000}
            max={99999999}
          />
        );

      default:
        return (
          <input
            type={field.type}
            name={field.name}
            value={formData[field.name] || ''}
            onChange={(e) => handleInputChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            className={commonClasses}
            required={field.required}
          />
        );
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`bg-white rounded-xl border border-gray-200 shadow-sm ${className}`}
    >
      <form onSubmit={handleSubmit} className="p-6 space-y-6">
        {fields.map((field, index) => (
          <motion.div
            key={field.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="space-y-2"
          >
            <label className="flex items-center space-x-2 text-sm font-medium text-gray-700">
              <span className="text-blue-500">{getFieldIcon(field.name)}</span>
              <span>{field.label}</span>
              {field.required && <span className="text-red-500">*</span>}
            </label>
            
            {renderField(field)}
            
            {errors[field.name] && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center space-x-1 text-red-600 text-sm"
              >
                <span>⚠️</span>
                <span>{errors[field.name]}</span>
              </motion.div>
            )}
          </motion.div>
        ))}

        <motion.button
          type="submit"
          disabled={isLoading}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className={`w-full py-3 px-6 rounded-lg font-medium transition-all duration-200 ${
            isLoading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-500 hover:bg-blue-600 active:bg-blue-700'
          } text-white shadow-lg hover:shadow-xl`}
        >
          {isLoading ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Processing...</span>
            </div>
          ) : (
            submitLabel
          )}
        </motion.button>
      </form>
    </motion.div>
  );
};

export default AppointmentForm;
