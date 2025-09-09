'use client'

import { useState, useEffect, useRef } from 'react'
import { MessageCircle, X, Send, Phone, MapPin } from 'lucide-react'
import { cn } from '@/lib/utils'

export function LiveChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot' as const,
      text: 'Hi there! 👋 I\'m Amal, your travel expert. How can I help you plan your dream trip today?',
      timestamp: typeof window !== 'undefined' ? new Date() : null,
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const botResponses = [
    'That sounds amazing! I can help you find the perfect package for that destination.',
    'Great choice! We have some incredible deals right now that would suit your plans.',
    'I\'d love to help you plan this trip! What\'s your preferred travel dates?',
    'Perfect! Let me check our current availability and best deals for you.',
    'That destination is absolutely stunning this time of year! We have customized packages starting from ₹15,000.',
    'Wonderful! I can arrange everything from flights to accommodation for your trip.',
    'Excellent choice! Would you like me to send you a detailed itinerary?',
    'I can definitely help with that! Let me prepare a personalized quote for you.',
  ]

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return

    const userMessage = {
      id: messages.length + 1,
      type: 'user' as const,
      text: inputMessage,
      timestamp: typeof window !== 'undefined' ? new Date() : null,
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsTyping(true)

    // Simulate bot response
    setTimeout(() => {
      const randomResponse = botResponses[Math.floor(Math.random() * botResponses.length)]
      const botMessage = {
        id: messages.length + 2,
        type: 'bot' as const,
        text: randomResponse,
        timestamp: typeof window !== 'undefined' ? new Date() : null,
      }
      setMessages(prev => [...prev, botMessage])
      setIsTyping(false)
    }, 1000 + Math.random() * 2000)
  }

  const handleQuickAction = (action: string) => {
    setInputMessage(action)
    setTimeout(() => handleSendMessage(), 100)
  }

  return (
    <>
      {/* Chat Widget Button */}
      <div className="fixed bottom-6 right-6 z-50">
        {!isOpen && (
          <button
            onClick={() => setIsOpen(true)}
            aria-label="Open chat"
            title="Chat with TripChoice"
            className="bg-ink hover:bg-accent-cool text-surface-light p-4 rounded-full shadow-e2 hover:shadow-e3 transition-all duration-250 focus:outline-none focus:ring-2 focus:ring-accent-cool/40"
          >
            <MessageCircle className="w-6 h-6" />
          </button>
        )}

        {/* Chat Widget */}
        {isOpen && (
          <div className="bg-white rounded-2xl shadow-e3 border border-cloud/20 w-80 h-96 flex flex-col animate-in slide-in-from-bottom-4 duration-300">
            {/* Header */}
            <div className="bg-gradient-to-r from-ink to-accent-cool text-surface-light p-4 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold">A</span>
                  </div>
                  <div>
                    <div className="font-semibold text-sm">Amal - Travel Expert</div>
                    <div className="text-xs opacity-90">● Online now</div>
                  </div>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="hover:bg-white/20 rounded-full p-1 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 p-4 space-y-4 overflow-y-auto">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    'flex',
                    message.type === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  <div
                    className={cn(
                      'max-w-[70%] p-3 rounded-2xl text-sm',
                      message.type === 'user'
                        ? 'bg-accent-cool text-surface-light rounded-br-sm'
                        : 'bg-slate-100 text-slate-800 rounded-bl-sm'
                    )}
                  >
                    {message.text}
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-slate-100 p-3 rounded-2xl rounded-bl-sm">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Quick Actions */}
            {messages.length === 1 && (
              <div className="px-4 pb-2">
                <div className="flex flex-wrap gap-2">
                  {['Plan my Kashmir trip', 'Beach holidays in Goa', 'Luxury Dubai experience'].map((action) => (
                    <button
                      key={action}
                      onClick={() => handleQuickAction(action)}
                      className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1 rounded-full transition-colors"
                    >
                      {action}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Input */}
            <div className="p-4 border-t border-slate-200">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask about your dream trip..."
                  className="flex-1 px-3 py-2 border border-slate-300 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-accent-cool focus:border-transparent"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim()}
                  className="bg-ink hover:bg-accent-cool disabled:bg-slate-300 disabled:cursor-not-allowed text-surface-light p-2 rounded-full transition-colors"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Contact Options */}
            <div className="px-4 pb-4 space-y-2">
              <button className="w-full flex items-center justify-center space-x-2 bg-ink hover:bg-accent-cool text-surface-light py-2 px-4 rounded-full text-sm font-medium transition-colors">
                <Phone className="w-4 h-4" />
                <span>Call +91 94470 03974</span>
              </button>

              <button className="w-full flex items-center justify-center space-x-2 bg-slate-100 hover:bg-slate-200 text-slate-700 py-2 px-4 rounded-full text-sm font-medium transition-colors">
                <MapPin className="w-4 h-4" />
                <span>Visit our office</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
