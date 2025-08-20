import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { HomeIcon, DashboardIcon, InfoIcon, MenuIcon, XIcon } from './common/Icons';

const NavBar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
  };

  const isActive = (path) => {
    return location.pathname === path;
  };

  const navItems = [
    {
      path: '/',
      label: 'Home',
      icon: HomeIcon
    },
    {
      path: '/dashboard',
      label: 'Dashboard',
      icon: DashboardIcon
    },
    {
      path: '/about',
      label: 'About',
      icon: InfoIcon
    }
  ];

  return (
    <nav className="navbar">
      <div className="nav-container">
        {/* Logo */}
        <Link to="/" className="nav-logo" onClick={closeMenu}>
          <span className="logo-icon">🏥</span>
          <span className="logo-text">MediScan-AI</span>
        </Link>

        {/* Desktop Navigation */}
        <div className={`nav-menu ${isMenuOpen ? 'active' : ''}`}>
          {navItems.map((item) => {
            const IconComponent = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
                onClick={closeMenu}
              >
                <IconComponent className="nav-icon" />
                {item.label}
              </Link>
            );
          })}
        </div>

        {/* Mobile Menu Toggle */}
        <button 
          className="nav-toggle"
          onClick={toggleMenu}
          aria-label="Toggle navigation menu"
          aria-expanded={isMenuOpen}
        >
          {isMenuOpen ? (
            <XIcon className="w-6 h-6" />
          ) : (
            <MenuIcon className="w-6 h-6" />
          )}
        </button>
      </div>

      {/* Mobile Menu Overlay */}
      {isMenuOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={closeMenu}
        />
      )}
    </nav>
  );
};

export default NavBar;
