/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ['class'],
    content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
		extend: {
			colors: {
			ink: '#071C3C',
			surface: '#FDFDF9',
			surfacePrimary: '#FDFDF9',
			slate: '#4A5365',
			cloud: '#AEB5BC',
			'ink-dark': '#071C3C',
			'surface-light': '#FDFDF9',
  			accent: {
  				warm: '#ED6B08',
  				cool: '#0647AE',
  				midnight: '#071C3C',
  				gold: '#D4AF37',
  				platinum: '#E5E4E2',
  				amber: '#FFBF00',
  				obsidian: '#0C0C0C'
  			},
  			background: 'hsl(var(--background))',
  			foreground: 'hsl(var(--foreground))',
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			primary: {
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			}
  		},
  		fontFamily: {
  			sans: [
  				"var(--font-inter)",
  				'system-ui',
  				'sans-serif'
  			],
  			display: [
  				"var(--font-fraunces)",
  				"var(--font-inter)",
  				'system-ui',
  				'sans-serif'
  			]
  		},
		fontSize: {
			// Display and headings
			'h1-desk': ['72px', { lineHeight: '1.05' }],
			'h1-mob': ['32px', { lineHeight: '1.1' }],
			'h1-small': ['28px', { lineHeight: '1.15' }],
			h2: ['40px', { lineHeight: '1.1' }],
			h3: ['28px', { lineHeight: '1.15' }],
			// Editorial
			'tile-title': ['22px', { lineHeight: '1.2' }],
			// Body text
			body: ['16px', { lineHeight: '1.6' }],
			small: ['14px', { lineHeight: '1.5' }],
			meta: ['12px', { lineHeight: '1.4' }],
		},
		// 8pt spacing tokens (aliases in spacing scale)
		spacing: {
			's8': '8px',
			's16': '16px',
			's24': '24px',
			's32': '32px',
			's48': '48px',
			's64': '64px',
			's96': '96px',
		},
  		borderRadius: {
  			sm: '12px',
  			md: '16px',
  			xl: '24px',
  			'2xl': '28px'
  		},
  		boxShadow: {
			e1: '0 1px 2px rgba(0,0,0,.06)',
			e2: '0 6px 16px rgba(7,28,60,.15)',
			e3: '0 18px 48px rgba(7,28,60,.18)',
			'premium-glow': '0 0 20px rgba(7, 28, 60, 0.3)',
			'hover-premium': '0 0 30px rgba(7, 28, 60, 0.4)'
  		},
  		animation: {
  			// Blueprint Motion System
  			'fade-in': 'fadeIn 0.25s cubic-bezier(.2,.8,.2,1)',
  			'slide-up': 'slideUp 0.25s cubic-bezier(.2,.8,.2,1)',
  			'scale-in': 'scaleIn 0.25s cubic-bezier(.2,.8,.2,1)',
  			'slide-in-left': 'slideInLeft 0.28s cubic-bezier(.2,.8,.2,1)',
  			'slide-in-right': 'slideInRight 0.28s cubic-bezier(.2,.8,.2,1)',

  			// Dopamine-Triggering Hover Effects
  			'hover-lift': 'hoverLift 0.25s cubic-bezier(.2,.8,.2,1)',
  			'hover-glow': 'hoverGlow 0.25s cubic-bezier(.2,.8,.2,1)',
  			'hover-pulse': 'hoverPulse 2s ease-in-out infinite',

  			// Achievement & Reward Animations
  			'achievement-pop': 'achievementPop 0.6s cubic-bezier(.68,-0.55,.265,1.55)',
  			'sparkle': 'sparkle 1.5s ease-in-out infinite',
  			'progress-fill': 'progressFill 1s cubic-bezier(.2,.8,.2,1)',

  			// Micro-Interactions
  			'heartbeat': 'heartbeat 1.5s ease-in-out infinite',
  			'shimmer': 'shimmer 2s cubic-bezier(.2,.8,.2,1)',
  			'float-gentle': 'floatGentle 3s ease-in-out infinite',
  			'wobble': 'wobble 0.8s cubic-bezier(.2,.8,.2,1)',

  			// Loading & Feedback
  			'spin-slow': 'spin 3s linear infinite',
  			'bounce-gentle': 'bounceGentle 2s ease-in-out infinite',
  			'ken-burns': 'kenBurns 18s ease-out forwards'
  		},
  		transitionDuration: {
  			'250': '250ms',
  		},
  		keyframes: {
  			// Entry Animations
  			fadeIn: {
  				'0%': { opacity: '0' },
  				'100%': { opacity: '1' }
  			},
  			slideUp: {
  				'0%': { transform: 'translateY(20px)', opacity: '0' },
  				'100%': { transform: 'translateY(0)', opacity: '1' }
  			},
  			scaleIn: {
  				'0%': { transform: 'scale(0.9)', opacity: '0' },
  				'100%': { transform: 'scale(1)', opacity: '1' }
  			},
  			slideInLeft: {
  				'0%': { transform: 'translateX(-30px)', opacity: '0' },
  				'100%': { transform: 'translateX(0)', opacity: '1' }
  			},
  			slideInRight: {
  				'0%': { transform: 'translateX(30px)', opacity: '0' },
  				'100%': { transform: 'translateX(0)', opacity: '1' }
  			},

  			// Dopamine Effects
  			hoverLift: {
  				'0%': { transform: 'translateY(0)' },
  				'100%': { transform: 'translateY(-8px)' }
  			},
  			hoverGlow: {
  				'0%': { boxShadow: '0 0 0 rgba(124, 58, 237, 0)' },
  				'100%': { boxShadow: '0 0 20px rgba(124, 58, 237, 0.4)' }
  			},
  			hoverPulse: {
  				'0%, 100%': { transform: 'scale(1)' },
  				'50%': { transform: 'scale(1.05)' }
  			},

  			// Achievement Effects
  			achievementPop: {
  				'0%': { transform: 'scale(0)', opacity: '0' },
  				'50%': { transform: 'scale(1.2)', opacity: '1' },
  				'100%': { transform: 'scale(1)', opacity: '1' }
  			},
  			sparkle: {
  				'0%, 100%': { opacity: '0', transform: 'scale(0.8)' },
  				'50%': { opacity: '1', transform: 'scale(1.2)' }
  			},
  			progressFill: {
  				'0%': { width: '0%' },
  				'100%': { width: '100%' }
  			},

  			// Micro-Interactions
  			heartbeat: {
  				'0%, 100%': { transform: 'scale(1)' },
  				'50%': { transform: 'scale(1.1)' }
  			},
  			shimmer: {
  				'0%': { transform: 'translateX(-100%)' },
  				'100%': { transform: 'translateX(100%)' }
  			},
  			floatGentle: {
  				'0%, 100%': { transform: 'translateY(0px)' },
  				'50%': { transform: 'translateY(-6px)' }
  			},
  			wobble: {
  				'0%, 100%': { transform: 'translateX(0%)' },
  				'15%': { transform: 'translateX(-25%) rotate(-5deg)' },
  				'30%': { transform: 'translateX(20%) rotate(3deg)' },
  				'45%': { transform: 'translateX(-15%) rotate(-3deg)' },
  				'60%': { transform: 'translateX(10%) rotate(2deg)' },
  				'75%': { transform: 'translateX(-5%) rotate(-1deg)' }
  			},

  			// Loading Effects
  			bounceGentle: {
  				'0%, 100%': { transform: 'translateY(0)' },
  				'50%': { transform: 'translateY(-10px)' }
  			},
  			kenBurns: {
  				'0%': { transform: 'scale(1.06)' },
  				'100%': { transform: 'scale(1)' }
  			}
  		}
  	}
  },
  plugins: [
    require('@tailwindcss/typography'),
    require("tailwindcss-animate"),
    function({ addUtilities }) {
      addUtilities({
        '.scrollbar-hide': {
          /* IE and Edge */
          '-ms-overflow-style': 'none',
          /* Firefox */
          'scrollbar-width': 'none',
          /* Safari and Chrome */
          '&::-webkit-scrollbar': {
            display: 'none'
          }
        },
        '.glass-card': {
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
        },
        '.btn-primary': {
          backgroundColor: '#071C3C',
          color: '#FDFDF9',
          fontWeight: '600',
          padding: '0.75rem 2rem',
          borderRadius: '9999px',
          transition: 'all 0.2s ease',
          '&:hover': {
            backgroundColor: '#0a285e',
            transform: 'translateY(-1px)'
          }
        },
        '.grain-overlay': {
          position: 'fixed',
          inset: '0',
          pointerEvents: 'none',
          backgroundImage:
            "radial-gradient(1px 1px at 10% 20%, rgba(7,28,60,.05) 1px, transparent 1px),radial-gradient(1px 1px at 30% 60%, rgba(6,71,174,.05) 1px, transparent 1px),radial-gradient(1px 1px at 70% 80%, rgba(74,83,101,.05) 1px, transparent 1px)",
          backgroundRepeat: 'repeat',
          backgroundSize: '64px 64px',
          opacity: '0.03',
          mixBlendMode: 'overlay'
        },
        // Glass header utility per spec (12px blur)
        '.glass-header': {
          background: 'rgba(253, 253, 249, 0.70)',
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          borderBottom: '1px solid rgba(174, 181, 188, 0.10)'
        },
        '.cinematic-grade': {
          filter: 'saturate(1.22) contrast(1.08) brightness(0.98)'
        },
        '.cinematic-grade-strong': {
          filter: 'saturate(1.35) contrast(1.12) brightness(0.96)'
        },
        // Gradient overlay utility used in cinematic hero
        '.cinematic-gradient': {
          backgroundImage: 'linear-gradient(to bottom, rgba(6, 71, 174, 0.15), rgba(7, 28, 60, 0.30) 50%, rgba(7, 28, 60, 0.75))'
        },
        // Elevation alias utilities (in addition to shadow-e*)
        '.elevation-e1': { boxShadow: '0 1px 2px rgba(7, 28, 60, 0.06)' },
        '.elevation-e2': { boxShadow: '0 6px 16px rgba(7, 28, 60, 0.15)' },
        '.elevation-e3': { boxShadow: '0 18px 48px rgba(7, 28, 60, 0.18)' }
      })
    }
  ],
}
