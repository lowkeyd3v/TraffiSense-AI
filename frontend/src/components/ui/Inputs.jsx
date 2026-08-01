import React from 'react';

export const TextInput = ({ label, placeholder, value, onChange, icon: Icon, type = 'text', required = false, name }) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
          {label} {required && <span className="text-rose-400">*</span>}
        </label>
      )}
      <div className="relative">
        {Icon && <Icon className="w-5 h-5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />}
        <input
          type={type}
          name={name}
          required={required}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          className={`w-full bg-slate-950 border border-slate-800 rounded-lg py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors ${
            Icon ? 'pl-10 pr-4' : 'px-4'
          }`}
        />
      </div>
    </div>
  );
};

export const SelectInput = ({ label, value, onChange, options = [], name }) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
          {label}
        </label>
      )}
      <select
        name={name}
        value={value}
        onChange={onChange}
        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
      >
        {options.map((opt) => (
          <option key={opt.value || opt} value={opt.value || opt}>
            {opt.label || opt}
          </option>
        ))}
      </select>
    </div>
  );
};