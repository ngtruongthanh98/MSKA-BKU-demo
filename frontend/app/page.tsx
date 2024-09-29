'use client';

import MyButton from "@/app/components/CustomButton";

export default function Home() {
  return (
    <div>
      <MyButton label="Click Me" onClick={() => alert('Button clicked!')} />
    </div>
  );
}
