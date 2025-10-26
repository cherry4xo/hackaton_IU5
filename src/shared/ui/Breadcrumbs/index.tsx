import React from 'react';
import { Link } from 'react-router-dom';
import styles from './Breadcrumbs.module.css';

interface BreadcrumbItem {
  label: string;
  path: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ items }) => {
  return (
    <nav className={styles.breadcrumbs}>
      {items.map((item, index) => (
        <span key={item.path} className={styles.breadcrumbItem}>
          {index < items.length - 1 ? (
            <Link to={item.path} className={styles.breadcrumbLink}>
              {item.label}
            </Link>
          ) : (
            <span className={styles.breadcrumbCurrent}>
              {item.label}
            </span>
          )}
          {index < items.length - 1 && (
            <span className={styles.separator}>›</span>
          )}
        </span>
      ))}
    </nav>
  );
};