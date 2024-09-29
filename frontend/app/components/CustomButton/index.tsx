'use client';

import React from 'react';
import './index.scss';

type MyButtonProps = {
  label: string;
  onClick: () => void;
};

const MyButton: React.FC<MyButtonProps> = ({ label, onClick }) => {
  return (
    <button className="my-button" onClick={onClick}>
      {label}
    </button>
  );
};

export default MyButton;
