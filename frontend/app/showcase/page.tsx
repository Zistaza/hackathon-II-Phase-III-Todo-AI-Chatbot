'use client';

import React from 'react';
import Link from 'next/link';
import { Button } from '../../components/ui/button';
import AnimatedButton from '../../components/ui/animated-button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import ThemeToggle from '../../components/ui/theme-toggle';

const ShowcasePage = () => {
  return (
    <div className="min-h-screen bg-background text-foreground py-12 px-4 sm:px-6">
      <div className="max-w-7xl mx-auto">
        <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 mb-12">
          <h1 className="text-4xl sm:text-5xl font-bold bg-gradient-to-r from-primary to-indigo-500 bg-clip-text text-transparent">
            Style & Animation Showcase
          </h1>
          <div className="flex items-center gap-6">
            <ThemeToggle />
            <Link href="/dashboard">
              <Button variant="secondary" size="lg">Back to Dashboard</Button>
            </Link>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-10">
          {/* Colors Section */}
          <Card className="hover-lift p-8">
            <CardHeader className="pb-6">
              <CardTitle className="text-2xl">Color Palette</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-primary"></div>
                    <span className="text-lg">Primary</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-secondary"></div>
                    <span className="text-lg">Secondary</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-accent"></div>
                    <span className="text-lg">Accent</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-destructive"></div>
                    <span className="text-lg">Destructive</span>
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-muted"></div>
                    <span className="text-lg">Muted</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-card"></div>
                    <span className="text-lg">Card</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full border-2 border-border"></div>
                    <span className="text-lg">Border</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-foreground"></div>
                    <span className="text-lg">Foreground</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Buttons Section */}
          <Card className="hover-lift p-8">
            <CardHeader className="pb-6">
              <CardTitle className="text-2xl">Buttons & Interactions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex flex-wrap gap-4">
                  <Button variant="primary" size="md">Primary</Button>
                  <Button variant="secondary" size="md">Secondary</Button>
                  <Button variant="danger" size="md">Danger</Button>
                </div>
                <div className="flex flex-wrap gap-4">
                  <AnimatedButton variant="default" size="md">Animated Primary</AnimatedButton>
                  <AnimatedButton variant="outline" size="md">Animated Secondary</AnimatedButton>
                  <AnimatedButton variant="ghost" size="md">Animated Danger</AnimatedButton>
                </div>
                <div className="flex flex-wrap gap-4">
                  <Button size="sm">Small</Button>
                  <Button size="md">Medium</Button>
                  <Button size="lg">Large</Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Animations Section */}
          <Card className="hover-lift p-8">
            <CardHeader className="pb-6">
              <CardTitle className="text-2xl">Animations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="animate-pulse p-4 bg-primary/10 rounded-xl text-center text-lg">Pulse</div>
                  <div className="animate-bounce p-4 bg-secondary/10 rounded-xl text-center text-lg">Bounce</div>
                  <div className="animate-float p-4 bg-accent/10 rounded-xl text-center text-lg">Float</div>
                </div>
                <div className="space-y-4">
                  <div className="animate-shimmer p-4 rounded-xl text-center text-base">Shimmer Effect</div>
                  <div className="animate-spin-slow p-4 bg-destructive/10 rounded-xl text-center flex items-center justify-center">
                    <div className="w-6 h-6 border-t-2 border-r-2 border-primary rounded-full"></div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Transitions Section */}
          <Card className="hover-lift p-8">
            <CardHeader className="pb-6">
              <CardTitle className="text-2xl">Transitions & Effects</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex flex-wrap gap-4">
                  <div className="p-4 bg-primary/10 rounded-xl hover-scale-105 cursor-pointer transition-all text-lg">Scale 105%</div>
                  <div className="p-4 bg-secondary/10 rounded-xl hover-lift cursor-pointer transition-all text-lg">Lift Effect</div>
                  <div className="p-4 bg-accent/10 rounded-xl hover-glow cursor-pointer transition-all text-lg">Glow Effect</div>
                  <div className="p-4 bg-destructive/10 rounded-xl btn-enhanced cursor-pointer transition-all text-lg">Enhanced Button</div>
                </div>

                <div className="p-6 bg-muted rounded-xl">
                  <p className="text-center text-base text-muted-foreground">This box demonstrates smooth transitions</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Typography Section */}
          <Card className="hover-lift p-8">
            <CardHeader className="pb-6">
              <CardTitle className="text-2xl">Typography</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <h1 className="text-5xl font-bold text-foreground">Heading 1</h1>
                <h2 className="text-4xl font-bold text-foreground">Heading 2</h2>
                <h3 className="text-3xl font-semibold text-foreground">Heading 3</h3>
                <p className="text-xl text-foreground">Large Paragraph Text</p>
                <p className="text-lg text-foreground">Regular Paragraph Text</p>
                <p className="text-base text-muted-foreground">Small Muted Text</p>
                <p className="text-sm text-muted-foreground/70">Extra Small Text</p>
              </div>
            </CardContent>
          </Card>

          {/* Shadows & Elevation */}
          <Card className="hover-lift p-8">
            <CardHeader className="pb-6">
              <CardTitle className="text-2xl">Shadows & Elevation</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-6">
                <div className="p-6 bg-card border rounded-xl shadow-sm text-center">Shadow SM</div>
                <div className="p-6 bg-card border rounded-xl shadow text-center">Shadow Regular</div>
                <div className="p-6 bg-card border rounded-xl shadow-md text-center">Shadow MD</div>
                <div className="p-6 bg-card border rounded-xl shadow-lg text-center">Shadow LG</div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="mt-16 text-center">
          <p className="text-xl text-muted-foreground">
            All styles, animations, and colors are now properly visible and functional!
          </p>
        </div>
      </div>
    </div>
  );
};

export default ShowcasePage;